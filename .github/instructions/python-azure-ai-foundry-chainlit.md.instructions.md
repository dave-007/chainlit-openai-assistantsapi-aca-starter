---
applyTo: '*.py;*.ipynb'
---
Coding standards, domain knowledge, and preferences that AI should follow.# GitHub Copilot Instructions - Azure AI Foundry & Chainlit Development

These instructions define how GitHub Copilot should assist with Azure AI Foundry and Chainlit development projects. The goal is to ensure consistent, high-quality code generation aligned with Azure AI Foundry best practices, Chainlit patterns, and conversational AI conventions.

## 🧠 Context

- **Project Type**: Azure AI Foundry Applications / Chainlit Chat Interfaces / Conversational AI / RAG Applications
- **Language**: Python
- **Primary Libraries**: chainlit / azure-ai-openai / azure-cognitiveservices / azure-ai-formrecognizer / azure-ai-textanalytics / langchain / semantic-kernel / azure-ai-foundry
- **Architecture**: Chainlit Apps / Azure AI Foundry Flows / RAG (Retrieval-Augmented Generation) / Multi-Agent Conversations

## 🔧 General Guidelines

- Use Pythonic patterns (PEP8, PEP257) with Azure AI Foundry and Chainlit conventions.
- Leverage async/await patterns for Azure service calls and Chainlit message handling.
- Use type hints extensively, especially for Azure client responses and Chainlit message types.
- Follow black or isort for formatting and import order.
- Use meaningful naming aligned with Azure AI Foundry terminology and Chainlit patterns.
- Emphasize conversational flow design and user experience in Chainlit applications.
- Implement proper error handling for Azure service limitations, throttling, and Chainlit session management.
- Implement proper retry logic and circuit breaker patterns for Azure AI Foundry flows.
- Structure applications around Chainlit's decorators and session management.

## 📁 File Structure

Use this structure as a guide when creating or updating Azure AI Foundry and Chainlit projects:

```text
src/
  app.py                # Main Chainlit application entry point
  chainlit/
    handlers/           # Chainlit message and action handlers
    components/         # Custom Chainlit UI components
    sessions/           # Session management and state
  foundry/
    flows/              # Azure AI Foundry flow definitions
    connections/        # Azure AI Foundry service connections
    models/             # Model configurations and deployments
  clients/              # Azure service clients and configuration
  services/             # Business logic and AI service orchestration
  agents/               # AI agents and multi-agent orchestration
  rag/                  # RAG implementation components
    retrieval/          # Document retrieval and search
    generation/         # Response generation logic
  prompts/              # Prompt templates and management
  utils/                # Helper functions and utilities
  config/               # Configuration and environment management
tests/
  unit/                 # Unit tests
  integration/          # Integration tests with Azure services
  chainlit/             # Chainlit-specific tests
  fixtures/             # Test data and mock responses
data/
  documents/            # Document store for RAG
  prompts/              # Stored prompt templates
  examples/             # Sample conversations and outputs
.chainlit/              # Chainlit configuration directory
  config.toml           # Chainlit configuration file
foundry/
  flows/                # Azure AI Foundry flow definitions
  data/                 # Training and evaluation data
```

## 🧶 Patterns

### ✅ Patterns to Follow

- Use Azure Identity (`DefaultAzureCredential`) for authentication in Azure AI Foundry.
- Implement proper connection pooling with Azure service clients.
- Use Pydantic models for request/response validation and Azure service responses.
- Structure Chainlit applications with proper decorators (`@cl.on_message`, `@cl.on_chat_start`, etc.).
- Implement session state management in Chainlit applications using `cl.user_session`.
- Use Azure AI Foundry flows for complex multi-step AI operations.
- Implement streaming responses in Chainlit for better user experience.
- Use Chainlit's built-in components (buttons, file uploads, etc.) for rich interactions.
- Implement structured logging with correlation IDs for tracing Azure service calls.
- Use environment variables for Azure service endpoints and keys via `python-dotenv`.
- Implement retry logic with exponential backoff for Azure service calls.
- Use async context managers for Azure client lifecycle management.
- Structure prompts as reusable templates with variable substitution.
- Implement proper error handling for Azure service-specific exceptions and Chainlit errors.
- Use dependency injection for Azure service clients within Chainlit handlers.
- Implement token usage tracking and cost monitoring for Azure AI Foundry deployments.
- Use Chainlit's authentication and user management features.
- Implement conversation memory and context management in Chainlit sessions.
- Use Azure AI Foundry's evaluation and monitoring capabilities.

### 🚫 Patterns to Avoid

- Don't hardcode Azure service endpoints, keys, or model names in Chainlit applications.
- Avoid blocking operations in Chainlit message handlers without proper async patterns.
- Don't ignore rate limiting and throttling responses from Azure services.
- Avoid exposing sensitive Azure service responses in Chainlit chat logs or error messages.
- Don't use wildcard imports, especially with Azure SDK modules.
- Avoid creating new Azure service clients for every Chainlit message.
- Don't ignore token usage and cost implications in AI service calls.
- Avoid storing sensitive data in Chainlit user sessions without proper encryption.
- Don't create overly complex Chainlit applications without proper separation of concerns.
- Avoid hardcoding Azure AI Foundry flow configurations.
- Don't neglect proper error handling in Chainlit message flows.
- Avoid mixing business logic directly in Chainlit decorators.

## 🔑 Azure AI Foundry & Chainlit Integration

### Chainlit Application Structure

```python
import chainlit as cl
from azure.ai.openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

# Initialize Azure AI client
@cl.on_chat_start
async def start():
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview"
    )
    cl.user_session.set("azure_client", client)

@cl.on_message
async def main(message: cl.Message):
    client = cl.user_session.get("azure_client")
    # Process message with Azure AI services
```

### Azure AI Foundry Flow Integration

```python
from azure.ai.foundry import AIFoundryClient
import chainlit as cl

@cl.on_message
async def handle_complex_query(message: cl.Message):
    foundry_client = cl.user_session.get("foundry_client")
    
    # Execute Azure AI Foundry flow
    flow_result = await foundry_client.flows.execute(
        flow_name="rag-qa-flow",
        inputs={"query": message.content}
    )
    
    await cl.Message(content=flow_result.output).send()
```

### Session State Management

```python
@cl.on_chat_start
async def init_session():
    # Initialize conversation context
    cl.user_session.set("conversation_history", [])
    cl.user_session.set("user_preferences", {})
    
@cl.on_message
async def maintain_context(message: cl.Message):
    history = cl.user_session.get("conversation_history", [])
    history.append({"role": "user", "content": message.content})
    cl.user_session.set("conversation_history", history)
```

### Authentication & Configuration

```python
from azure.identity import DefaultAzureCredential
from azure.ai.openai import AzureOpenAI
import os

# Preferred authentication method
credential = DefaultAzureCredential()

# Client configuration
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)
```

### Error Handling

```python
from azure.core.exceptions import (
    HttpResponseError, 
    ResourceNotFoundError, 
    ServiceRequestError
)

try:
    response = await client.chat.completions.create(...)
except HttpResponseError as e:
    # Handle rate limiting, quota exceeded, etc.
    logger.error(f"Azure AI service error: {e.status_code} - {e.message}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

## 🧪 Testing Guidelines

- Use `pytest` with `pytest-asyncio` for testing async Azure service calls.
- Mock Azure service responses using `azure-core-tracing-opentelemetry` or custom mocks.
- Use fixtures for Azure client setup and test data preparation.
- Test both successful responses and various Azure service error conditions.
- Implement integration tests with Azure service emulators when available.
- Test token usage tracking and cost calculation logic.
- Validate prompt template rendering and variable substitution.

## 🧩 Example Prompts

- `Copilot, create a Chainlit application with Azure OpenAI integration and streaming responses.`
- `Copilot, implement a Chainlit chat handler that uses Azure AI Foundry flows for document Q&A.`
- `Copilot, write a Chainlit session management system that maintains conversation context.`
- `Copilot, create a Chainlit application with file upload functionality for document analysis using Azure AI Document Intelligence.`
- `Copilot, implement a multi-agent conversation system in Chainlit with Azure AI Foundry orchestration.`
- `Copilot, write a RAG implementation using Chainlit, Azure Cognitive Search, and Azure OpenAI with streaming.`
- `Copilot, create a Chainlit authentication system integrated with Azure Active Directory.`
- `Copilot, implement a Chainlit chatbot with custom UI components and Azure AI service error handling.`
- `Copilot, write an Azure AI Foundry flow that processes user inputs and returns structured responses for Chainlit.`
- `Copilot, create a Chainlit application with conversation memory and user preference persistence.`

## 🔍 Monitoring & Observability

- Implement structured logging with Azure service correlation IDs and Chainlit session tracking.
- Track token usage, response times, and error rates across Azure AI Foundry flows.
- Use Azure Application Insights for telemetry and monitoring of both backend services and Chainlit applications.
- Implement health check endpoints for Azure service connectivity and Chainlit application status.
- Monitor conversation flows and user interactions in Chainlit applications.
- Log Azure AI Foundry flow execution metrics and performance data.
- Track user engagement metrics and conversation completion rates in Chainlit.
- Implement custom metrics for RAG retrieval accuracy and relevance scoring.
- Monitor Azure AI Foundry model performance and drift detection.
- Use Chainlit's built-in analytics and conversation tracking features.

## 🔁 Iteration & Review

- Review Copilot output for Azure AI Foundry best practices and Chainlit patterns.
- Validate error handling covers Azure-specific exceptions, rate limiting, and Chainlit session errors.
- Ensure proper resource cleanup and connection management in both Azure services and Chainlit.
- Test Chainlit conversation flows and user experience across different scenarios.
- Verify Azure AI Foundry flow integration and proper error propagation to Chainlit UI.
- Test Azure service integration with appropriate mocking strategies for Chainlit applications.
- Verify compliance with Azure AI responsible AI guidelines in Chainlit conversations.
- Check for proper handling of sensitive data in prompts, responses, and Chainlit sessions.
- Review Chainlit UI/UX patterns and accessibility considerations.
- Validate Azure AI Foundry flow performance and optimization.

## 📚 References

- [Chainlit Documentation](https://docs.chainlit.io/)
- [Azure AI Foundry Documentation](https://docs.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Foundry SDK for Python](https://pypi.org/project/azure-ai-foundry/)
- [Chainlit Examples and Cookbook](https://github.com/Chainlit/chainlit/tree/main/examples)
- [Azure AI Services Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/)
- [Azure OpenAI Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure SDK for Python](https://docs.microsoft.com/en-us/azure/developer/python/)
- [Azure Identity Library](https://docs.microsoft.com/en-us/python/api/azure-identity/)
- [LangChain Azure Integration](https://python.langchain.com/docs/integrations/platforms/microsoft)
- [Semantic Kernel for Python](https://github.com/microsoft/semantic-kernel)
- [Azure Cognitive Search](https://docs.microsoft.com/en-us/azure/search/)
- [Azure AI Document Intelligence](https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/)
- [Azure Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Azure AI Responsible AI Guidelines](https://docs.microsoft.com/en-us/azure/cognitive-services/responsible-use-of-ai-overview)
- [Chainlit Authentication](https://docs.chainlit.io/authentication/overview)
- [Chainlit Custom Components](https://docs.chainlit.io/custom-components/overview)