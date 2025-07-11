# Migration Guide: OpenAI Assistant API to Azure AI Projects/Agents

This guide helps you migrate from the direct OpenAI Assistant API implementation to Azure AI Projects and Azure AI Agents SDKs.

## Overview

The refactored implementation provides:
- **Better Azure Integration**: Native Azure authentication and project management
- **Unified SDK**: Single SDK for agent management, file handling, and streaming
- **Enhanced Security**: Uses Azure DefaultAzureCredential instead of API keys
- **Simplified Deployment**: Better integration with Azure infrastructure

## Files Changed

| Original File | New File | Purpose |
|---------------|----------|---------|
| `src/app.py` | `src/app_azure.py` | Main Chainlit application with Azure AI integration |
| `src/create_assistant.py` | `src/create_agent_azure.py` | Agent/Assistant creation script |
| N/A | `src/.env.template` | Environment variables template for Azure AI |

## Key Code Changes

### 1. Import Statements

**Before (OpenAI):**
```python
from openai import AsyncAssistantEventHandler, AsyncOpenAI, OpenAI
from openai.types.beta.threads.runs import RunStep
```

**After (Azure AI):**
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep
)
```

### 2. Client Initialization

**Before (OpenAI):**
```python
async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
sync_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
assistant = sync_openai_client.beta.assistants.retrieve(os.environ.get("OPENAI_ASSISTANT_ID"))
```

**After (Azure AI):**
```python
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ.get("PROJECT_ENDPOINT")
)
agents_client = project_client.agents
agent = agents_client.get_agent(os.environ.get("AZURE_AGENT_ID"))
```

### 3. Event Handler

**Before (OpenAI):**
```python
class EventHandler(AsyncAssistantEventHandler):
    # Implementation using OpenAI event types
```

**After (Azure AI):**
```python
class EventHandler(AgentEventHandler):
    # Implementation using Azure AI event types
```

### 4. File Operations

**Before (OpenAI):**
```python
uploaded_file = await async_openai_client.files.create(
    file=Path(file.path), purpose="assistants"
)
response = await async_openai_client.files.with_raw_response.content(file_id)
```

**After (Azure AI):**
```python
uploaded_file = await agents_client.upload_file(
    file_path=file.path, purpose="assistants"
)
response = await agents_client.get_file_content(file_id)
```

### 5. Thread and Message Operations

**Before (OpenAI):**
```python
thread = await async_openai_client.beta.threads.create()
message = await async_openai_client.beta.threads.messages.create(
    thread_id=thread_id, role="user", content=content
)
```

**After (Azure AI):**
```python
thread = await agents_client.create_thread()
message = await agents_client.create_message(
    thread_id=thread_id, role="user", content=content
)
```

### 6. Streaming

**Before (OpenAI):**
```python
async with async_openai_client.beta.threads.runs.stream(
    thread_id=thread_id,
    assistant_id=assistant.id,
    event_handler=EventHandler(assistant_name=assistant.name),
) as stream:
    await stream.until_done()
```

**After (Azure AI):**
```python
async with agents_client.create_stream(
    thread_id=thread_id,
    agent_id=agent.id,
    event_handler=EventHandler(assistant_name=agent.name),
) as stream:
    await stream.until_done()
```

## Environment Variables Migration

### Before (OpenAI)
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_ASSISTANT_ID=asst_...
DATABASE_URL=postgresql://...
LITERAL_API_KEY=...
```

### After (Azure AI)
```env
PROJECT_ENDPOINT=https://your-project.eastus.ai.azure.com
AZURE_AGENT_ID=agent_...
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
DATABASE_URL=postgresql://...
LITERAL_API_KEY=...
```

## Authentication Setup

The Azure AI version uses `DefaultAzureCredential`, which automatically handles authentication through:

1. **Azure CLI**: `az login`
2. **Environment Variables**: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
3. **Managed Identity**: When running in Azure
4. **Visual Studio Code**: Azure Account extension
5. **Azure PowerShell**: `Connect-AzAccount`

## Prerequisites for Migration

1. **Azure AI Project**: Create an Azure AI Foundry Project
2. **Agent Creation**: Use `create_agent_azure.py` to create your agent
3. **Model Deployment**: Ensure you have Azure OpenAI model deployments
4. **Authentication**: Set up Azure authentication (Azure CLI recommended for development)

## Testing the Migration

1. **Install Dependencies**: Ensure `azure-ai-projects` and `azure-ai-agents` are installed
2. **Set Environment Variables**: Use the new Azure AI environment variables
3. **Create Agent**: Run `python create_agent_azure.py` to create your agent
4. **Test Application**: Run `chainlit run app_azure.py -w` to test the new implementation

## Rollback Plan

If you need to rollback to the OpenAI implementation:
1. Use the original `app.py` and `create_assistant.py` files
2. Set the original OpenAI environment variables
3. Run `chainlit run app.py -w`

## Benefits of Migration

- **Better Azure Integration**: Native Azure project management
- **Enhanced Security**: No need to store API keys, uses Azure authentication
- **Unified SDK**: Single SDK for all AI operations
- **Better Error Handling**: More comprehensive error handling and logging
- **Future-Proof**: Better support for new Azure AI features

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure you're logged into Azure CLI with `az login`
2. **Project Endpoint**: Verify your `PROJECT_ENDPOINT` URL is correct
3. **Agent Not Found**: Check that your `AZURE_AGENT_ID` exists in the project
4. **Model Deployment**: Ensure your `MODEL_DEPLOYMENT_NAME` is deployed in your Azure OpenAI resource

### Getting Help

- Check Azure AI Project logs in the Azure portal
- Verify your Azure role assignments (AI Developer or Cognitive Services Contributor)
- Test authentication with `az account show`