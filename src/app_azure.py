import os
import plotly
from pathlib import Path
from typing import List, Dict, Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
#     CodeInterpreterToolOutput,
#     FileSearchToolOutput
)

from literalai.helper import utc_now

import chainlit as cl
from chainlit.config import config
from chainlit.element import Element
from chainlit.context import local_steps


# Initialize Azure AI Project Client
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ.get("AIPROJECT_ENDPOINT", "")  # Using AIPROJECT_ENDPOINT from .env with empty default
)
# -- Azure AI Projects Examples -------------------------------------------
# # List project flows
# # flows = project_client.flows.list()
# # for flow in flows:
# #     print(flow.name, flow.id)
# 
# # Execute a specific flow
# # result = await project_client.flows.execute(
# #     flow_name="example-flow", inputs={"key": "value"}
# # )
# # print(result.output)
# 
# # Upload assistant file
# # upload = project_client.file_uploads.create(
# #     file=open("data.csv","rb"), purpose="assistants"
# # )
# -- End Azure AI Projects Examples ---------------------------------------

# Get the agents client
agents_client = project_client.agents
# -- Azure AI Agents Examples ---------------------------------------------
# # List all agents
# # agents = agents_client.list_agents()
# # for ag in agents:
# #     print(ag.id, ag.name)
# 
# # Create a new agent
# # new_agent = agents_client.create_agent(
# #     model="gpt-4o", name="Sample", instructions="..."
# # )
# # print(new_agent.id)
# 
# # Retrieve agent details
# # agent_info = agents_client.get_agent(new_agent.id)
# # print(agent_info.model)
# -- End Azure AI Agents Examples -----------------------------------------

# Retrieve the assistant/agent
agent = agents_client.get_agent(os.environ.get("ASSISTANT_ID", ""))  # Using ASSISTANT_ID from .env with empty default

config.ui.name = agent.name

class EventHandler(AgentEventHandler):

    def __init__(self, assistant_name: str) -> None:
        super().__init__()
        self.current_message: cl.Message = None
        self.current_step: cl.Step = None
        self.current_tool_call = None
        self.assistant_name = assistant_name
        previous_steps = local_steps.get() or []
        parent_step = previous_steps[-1] if previous_steps else None
        if parent_step:
            self.parent_id = parent_step.id

    async def on_run_step_created(self, run_step: RunStep) -> None:
        cl.user_session.set("run_step", run_step)

    async def on_text_created(self, text) -> None:
        self.current_message = await cl.Message(author=self.assistant_name, content="").send()

    async def on_text_delta(self, delta, snapshot):
        if delta.value:
            await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text):
        await self.current_message.update()
        if text.annotations:
            for annotation in text.annotations:
                if annotation.type == "file_path":
                    # Get file content from Azure AI Projects
                    file_content = await agents_client.get_file_content(annotation.file_path.file_id)
                    file_name = annotation.text.split("/")[-1]
                    try:
                        fig = plotly.io.from_json(file_content)
                        element = cl.Plotly(name=file_name, figure=fig)
                        await cl.Message(
                            content="",
                            elements=[element]).send()
                    except Exception as e:
                        element = cl.File(content=file_content, name=file_name)
                        await cl.Message(
                            content="",
                            elements=[element]).send()
                    # Hack to fix links
                    if annotation.text in self.current_message.content and element.chainlit_key:
                        self.current_message.content = self.current_message.content.replace(annotation.text, f"/project/file/{element.chainlit_key}?session_id={cl.context.session.id}")
                        await self.current_message.update()

    async def on_tool_call_created(self, tool_call):
        self.current_tool_call = tool_call.id
        self.current_step = cl.Step(name=tool_call.type, type="tool", parent_id=self.parent_id)
        self.current_step.show_input = "python"
        self.current_step.start = utc_now()
        await self.current_step.send()

    async def on_tool_call_delta(self, delta, snapshot): 
        if snapshot.id != self.current_tool_call:
            self.current_tool_call = snapshot.id
            self.current_step = cl.Step(name=delta.type, type="tool", parent_id=self.parent_id)
            self.current_step.start = utc_now()
            if snapshot.type == "code_interpreter":
                 self.current_step.show_input = "python"
            if snapshot.type == "function":
                self.current_step.name = snapshot.function.name
                self.current_step.language = "json"
            await self.current_step.send()
        
        if delta.type == "function":
            pass
        
        if delta.type == "code_interpreter":
            if delta.code_interpreter.outputs:
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.current_step.output += output.logs
                        self.current_step.language = "markdown"
                        self.current_step.end = utc_now()
                        await self.current_step.update()
                    elif output.type == "image":
                        self.current_step.language = "json"
                        self.current_step.output = output.image.model_dump_json()
            else:
                if delta.code_interpreter.input:
                    await self.current_step.stream_token(delta.code_interpreter.input, is_input=True)  

    async def on_event(self, event) -> None:
        if event.event == "error":
            return cl.ErrorMessage(content=str(event.data.message)).send()

    async def on_exception(self, exception: Exception) -> None:
        return cl.ErrorMessage(content=str(exception)).send()

    async def on_tool_call_done(self, tool_call):       
        self.current_step.end = utc_now()
        await self.current_step.update()

    async def on_image_file_done(self, image_file):
        image_id = image_file.file_id
        response = await agents_client.get_file_content(image_id)
        image_element = cl.Image(
            name=image_id,
            content=response,
            display="inline",
            size="large"
        )
        if not self.current_message.elements:
            self.current_message.elements = []
        self.current_message.elements.append(image_element)
        await self.current_message.update()


@cl.step(type="tool")
async def speech_to_text(audio_file):
    # Using Azure AI Projects for speech-to-text
    with project_client.inference.get_azure_openai_client() as openai_client:
        response = await openai_client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    return response.text


async def upload_files(files: List[Element]):
    file_ids = []
    for file in files:
        uploaded_file = await agents_client.upload_file(
            file_path=file.path, purpose="assistants"
        )
        file_ids.append(uploaded_file.id)
    return file_ids


async def process_files(files: List[Element]):
    # Upload files if any and get file_ids
    file_ids = []
    if len(files) > 0:
        file_ids = await upload_files(files)

    return [
        {
            "file_id": file_id,
            "tools": [{"type": "code_interpreter"}, {"type": "file_search"}] if file.mime in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/markdown", "application/pdf", "text/plain"] else [{"type": "code_interpreter"}],
        }
        for file_id, file in zip(file_ids, files)
    ]


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Run Tesla stock analysis",
            message="Make a data analysis on the tesla-stock-price.csv file I previously uploaded.",
            icon="/public/write.svg",
            ),
        cl.Starter(
            label="Run a data analysis on my CSV",
            message="Make a data analysis on the next CSV file I will upload.",
            icon="/public/write.svg",
            )
        ]

@cl.on_chat_start
async def greet_user():
    # send a simple welcome message
    await cl.Message(
        content="👋 Welcome to AURA! Ask me anything or upload a file to get started."
    ).send()
    
async def start_chat():
    # Create a Thread using Azure AI Agents
    thread = await agents_client.create_thread()
    # Store thread ID in user session for later use
    cl.user_session.set("thread_id", thread.id)
    
    app_user = cl.user_session.get("user")
    await cl.Message(f"Hello {app_user.identifier}").send()
    
    
@cl.on_stop
async def stop_chat():
    current_run_step: RunStep = cl.user_session.get("run_step")
    if current_run_step:
        await agents_client.cancel_run(thread_id=current_run_step.thread_id, run_id=current_run_step.run_id)


@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    attachments = await process_files(message.elements)

    # Add a Message to the Thread
    thread_message = await agents_client.create_message(
        thread_id=thread_id,
        role="user",
        content=message.content,
        attachments=attachments,
    )

    # Create and Stream a Run
    async with agents_client.create_stream(
        thread_id=thread_id,
        agent_id=agent.id,
        event_handler=EventHandler(assistant_name=agent.name),
    ) as stream:
        await stream.until_done()

@cl.oauth_callback
async def oauth_callback(
    provider_id: str,
    token: str,
# Removed duplicate empty handlers to avoid overriding configured callbacks
async def on_chat_resume(thread):
    pass

@cl.on_message
async def on_message(message):
    pass

# Audio chunk handler: transcribe audio and send transcript
@cl.on_audio_chunk
async def on_audio_chunk(audio_file):
    # Use speech_to_text step to transcribe audio
    transcript = await speech_to_text(audio_file)
    # Send the transcription back to the chat
    await cl.Message(content=transcript).send()
