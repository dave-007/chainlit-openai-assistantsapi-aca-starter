from dotenv import load_dotenv
load_dotenv()

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize Azure AI Project Client
project_endpoint = os.environ.get("PROJECT_ENDPOINT")
if not project_endpoint:
    raise ValueError("The environment variable 'PROJECT_ENDPOINT' must be set.")

project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=project_endpoint
)

# Get the agents client
agents_client = project_client.agents

instructions = """You are an assistant running data analysis on CSV files.

You will use code interpreter to run the analysis.

However, instead of rendering the charts as images, you will generate a plotly figure and turn it into json.
You will create a file for each json that I can download through annotations.
"""

# Upload the CSV file for the assistant
# Use the correct client and method to upload file resources
# For CSVs you’ll typically use project_file_type="Table" (you can change this if needed)
with open("../data/sku1.csv", "rb") as f:
    uploaded_file = project_client.file_resources.create(
        file=f,
        name="sku1.csv",
        project_file_type="Table"  # e.g. "Table" for CSV; or "Document"/other as appropriate
    )

# Create the agent with tools and file resources
agent = agents_client.create_agent(
    model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
    name="Data Analysis Assistant",
    instructions=instructions,
    tools=[
        {"type": "code_interpreter"},
        {"type": "file_search"}
    ],
    tool_resources={
        "code_interpreter": {
            "file_ids": [uploaded_file.id]
        }
    }
)

print(f"Agent created with id: {agent.id}")
print(f"Agent name: {agent.name}")
print(f"Model: {agent.model}")