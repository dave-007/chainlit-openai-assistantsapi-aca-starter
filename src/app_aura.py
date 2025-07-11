import os
import json
import asyncio
import chainlit as cl
import logging
from dotenv import load_dotenv
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    FilePurpose,
    FileSearchTool,
    ListSortOrder,
    RunAdditionalFieldList,
    RunStepFileSearchToolCall,
    RunStepToolCallDetails,
    ThreadMessageOptions, 
    MessageRole,
    AzureAISearchTool,
    AzureAISearchQueryType
)
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
from pprint import pprint

from wsproto import ConnectionType

# Load environment variables
load_dotenv()

# Disable verbose connection logs
logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

PROJECT_ENDPOINT = os.getenv("AIPROJECT_ENDPOINT")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# We'll initialize the client in the on_chat_start handler to ensure it's created in the async context
project_client = None
agents_client = None

# Chainlit setup
import chainlit as cl

@cl.set_starters
async def set_starters(user: cl.User | None):
    return [
        cl.Starter(
            label="Which SPD is right for PoE Mode A applications?",
            message="Which SPD is right for PoE Mode A applications?",
            icon="lightning"
        ),
        cl.Starter(
            label="Can the I2R-75KD480 protect a 480V VFD?",
            message="Can the I2R-75KD480 protect a 480V VFD?",
            icon="shield"
        ),
        cl.Starter(
            label="What cable pairs best with the DPR-F140 for an outdoor PoE++ install?",
            message="What cable pairs best with the DPR-F140 for an outdoor PoE++ install?",
            icon="cable"
        ),
        cl.Starter(
            label="Need an RF coax protector for a 900 MHz antenna with N-Type connectors?",
            message="Need an RF coax protector for a 900 MHz antenna with N-Type connectors?",
            icon="shield"
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    # Instantiate the AI assistant client
    global project_client, agents_client
    credential = DefaultAzureCredential()
    if not PROJECT_ENDPOINT:
        raise ValueError("AIPROJECT_ENDPOINT environment variable is not set.")
    # Create clients that will be properly managed
    
    # Initialize the project client
    project_client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

    
    connections = project_client.connections.list()
    async for cs in connections:
        pprint(vars(cs))
    
    default_connection = await project_client.connections.get_default("CognitiveSearch")
    conn_id = default_connection.id
    print(f"Default Connection ID: {conn_id}")
    
    
     # Initialize agent AI search tool and add the search index connection id
    ai_search = AzureAISearchTool(
        index_connection_id=conn_id,
        index_name="azureblob-index",
        query_type=AzureAISearchQueryType.SIMPLE,
        top_k=3,
        filter="",
    )

    # # List all connections and dump as JSON
    # connections = project_client.connections.list()
    # print(json.dumps(connections, indent=2))

    # # Get the default connection
    # conn = await project_client.connections.get_default()
    # conn_id = conn.id
    # print(f"Connection ID: {conn_id}")
    
    # Initialize the agents client
    agents_client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)


    # Verify the assistant exists by trying to get it
    try:
        # Check if ASSISTANT_ID is set
        if not ASSISTANT_ID:
            raise ValueError("ASSISTANT_ID environment variable is not set.")
        assistant = await agents_client.get_agent(agent_id=ASSISTANT_ID)
        print(f"Connected to agent: {assistant.name} (ID: {assistant.id})")
    except Exception as e:
        raise ValueError(f"Assistant with ID {ASSISTANT_ID} not found or could not be accessed: {str(e)}")

    # List existing vector stores
    vector_stores = agents_client.vector_stores.list()
    print("Existing Vector Stores:")
    async for vs in vector_stores:
        print(f" - {vs.name} (ID: {vs.id})")
    


    # Reference existing vector store by ID
    vector_store_id = os.getenv("ASSISTANT_VECTOR_STORE_ID")
    if not vector_store_id:
        raise ValueError("ASSISTANT_VECTOR_STORE_ID environment variable is not set.")
    vector_store = await agents_client.vector_stores.get(vector_store_id=vector_store_id)


    # List vector store contents
    print(f"Contents of Vector Store {vector_store_id}:")
    pprint(vars(vector_store))

    # List project  datasets contents
    print(f"Contents of Project datasets:")
    datasets = project_client.datasets.list()
    async for ds in datasets:
        pprint(vars(ds))

    # List project  index contents
    print(f"Contents of Project indexes:")
    indexes = project_client.indexes.list()
    async for idx in indexes:
        pprint(vars(idx))

    # Create file search tool with resources followed by creating agent
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])
    print(f"Contents of File Search Tool:")
    pprint(vars(file_search))

    # Update the agent's system instructions using the contents of ASSISTANT-INSTRUCTIONS.MD
    instructions_path = os.path.join(os.path.dirname(__file__), "../data/ASSISTANT-INSTRUCTIONS.MD")
    if os.path.exists(instructions_path):
        with open(instructions_path, "r", encoding="utf-8") as f:
            system_instructions = f.read()
        # Update the agent's instructions
        await agents_client.update_agent(
            agent_id=ASSISTANT_ID,
            instructions=system_instructions,
            tools=ai_search.definitions,
            tool_resources=ai_search.resources
            )
    else:
        print(f"Instructions file not found at {instructions_path}")
    # Store the clients in user session for proper lifecycle management
    cl.user_session.set("project_client", project_client)
    cl.user_session.set("agents_client", agents_client)

    # Create a new thread for this conversation
    if not cl.user_session.get("thread_id"):
        thread = await agents_client.threads.create()
        cl.user_session.set("thread_id", thread.id)
        print(f"New Thread ID: {thread.id}")

@cl.on_message
async def on_message(message: cl.Message):
    global agents_client
    
    thread_id = cl.user_session.get("thread_id")
    if not thread_id:
        await cl.Message(content="No active thread. Please refresh the page.").send()
        return
    
    if not ASSISTANT_ID:
        await cl.Message(content="ASSISTANT_ID environment variable is not set.").send()
        return
        
    if not agents_client:
        # Re-initialize if needed
        credential = DefaultAzureCredential()
        if not PROJECT_ENDPOINT:
            await cl.Message(content="AIPROJECT_ENDPOINT environment variable is not set.").send()
            return
            
        # Create new clients
        project_client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
        agents_client = AgentsClient(endpoint=PROJECT_ENDPOINT, credential=credential)
        
        # Update the session
        cl.user_session.set("project_client", project_client)
        cl.user_session.set("agents_client", agents_client)
    
    try:
        # Show thinking message to user
        thinking_msg = await cl.Message(content="thinking...", author="assistant").send()

        # Add the user message to the thread
        await agents_client.messages.create(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=message.content
        )
        
        # Run the assistant to process the message in the thread
        run = await agents_client.runs.create(
            thread_id=thread_id, 
            agent_id=ASSISTANT_ID
        )
        
        # Poll until run is complete
        while run.status in ["queued", "in_progress", "requires_action"]:
            await asyncio.sleep(1)
            run = await agents_client.runs.get(
                thread_id=thread_id,
                run_id=run.id
            )
            print(f"Run status: {run.status}")
            
        print(f"Run finished with status: {run.status}")

        # Check if you got an error
        if run.status == "failed":
            error_message = "Run failed"
            if hasattr(run, 'last_error'):
                if hasattr(run.last_error, 'message'):
                    error_message = run.last_error.message
                elif hasattr(run.last_error, 'code'):
                    error_message = f"Error code: {run.last_error.code}"
            raise Exception(error_message)

        # Get all messages from the thread
        messages = agents_client.messages.list(
            thread_id=thread_id,
            order=ListSortOrder.DESCENDING  # Get newest messages first
        )
        
        # Find the latest assistant message
        assistant_message = None
        async for msg in messages:
            if msg.role == MessageRole.AGENT:  # In the new API, assistants have the role "agent"
                assistant_message = msg
                break
                
        if not assistant_message:
            raise Exception("No response from the assistant.")
        
        # Extract text from the message
        message_text = ""
        if hasattr(assistant_message, 'text_messages') and assistant_message.text_messages:
            for content in assistant_message.text_messages:
                if hasattr(content, 'text'):
                    message_text += content.text.value
        
        # Update the Chainlit message with the assistant's response
        thinking_msg.content = message_text
        await thinking_msg.update()

    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()

@cl.on_chat_end
async def on_chat_end():
    # Clean up resources when the session ends
    project_client = cl.user_session.get("project_client")
    agents_client = cl.user_session.get("agents_client")
    
    # Close the clients properly
    if project_client:
        await project_client.close()
    if agents_client:
        await agents_client.close()
    
    print("Client sessions closed properly")

if __name__ == "__main__":
    # Chainlit will automatically run the application
    pass