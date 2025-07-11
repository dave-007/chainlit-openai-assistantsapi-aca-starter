# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chainlit application that uses Azure AI Projects and Azure AI Agents to create an AI-powered data analysis assistant. The app is containerized and designed to deploy on Azure Container Apps using Azure Developer CLI (azd).

**Key Components:**
- **Chainlit**: Interactive chat interface for AI assistants
- **Azure AI Projects**: Unified AI project management and deployment
- **Azure AI Agents**: Agent creation and management with streaming capabilities
- **PostgreSQL + Prisma**: Database layer for conversation/thread persistence
- **Azure Container Apps**: Cloud hosting platform
- **Docker**: Containerization for deployment

## Architecture

The application follows a three-tier architecture:
1. **Frontend**: Chainlit web interface (`src/app_azure.py`)
2. **Backend**: Azure AI Projects and Agents integration with event streaming
3. **Database**: PostgreSQL with Prisma ORM for conversation logging

**Key Files:**
- `src/app_azure.py`: Main application with Azure AI integration (refactored)
- `src/app.py`: Original OpenAI Assistant integration (legacy)
- `src/create_agent_azure.py`: Agent creation using Azure AI SDKs
- `src/create_assistant.py`: Original OpenAI Assistant creation (legacy)
- `prisma/schema.prisma`: Database schema for conversation logging
- `src/dockerfile`: Multi-stage Docker build
- `azure.yaml`: Azure deployment configuration
- `infra/`: Bicep templates for Azure infrastructure

## Development Commands

### Local Development
```bash
# Navigate to src directory
cd src

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Azure AI version
chainlit run app_azure.py -w

# Or run the legacy OpenAI version
chainlit run app.py -w
```

### Docker Development
```bash
# Build Docker image
docker build -t chainlit-local src/

# Run container with Azure AI environment variables
docker run -d -p 8080:8080 \
  -e PROJECT_ENDPOINT=https://your-project.eastus.ai.azure.com \
  -e AZURE_AGENT_ID=your_agent_id \
  -e MODEL_DEPLOYMENT_NAME=gpt-4o-mini \
  chainlit-local
```

### Database Operations
```bash
# Generate Prisma client
npx prisma generate

# Apply database migrations
npx prisma migrate dev

# View database in browser
npx prisma studio
```

### Azure Deployment
```bash
# Login to Azure
azd auth login

# Deploy to Azure (provisions infrastructure and deploys)
azd up

# Deploy code changes only
azd deploy
```

### Agent Management
```bash
# Create a new agent (Azure AI version)
cd src
python create_agent_azure.py

# Create a new assistant (legacy OpenAI version)
python create_assistant.py
```

## Environment Variables

### Azure AI Version (Recommended)
Required environment variables:
- `PROJECT_ENDPOINT`: Azure AI Project endpoint URL
- `AZURE_AGENT_ID`: Azure AI Agent ID
- `MODEL_DEPLOYMENT_NAME`: Azure OpenAI model deployment name
- `DATABASE_URL`: PostgreSQL connection string
- `LITERAL_API_KEY`: (Optional) For enhanced logging

Azure authentication is handled automatically via `DefaultAzureCredential`.

### Legacy OpenAI Version
Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_ASSISTANT_ID`: OpenAI Assistant ID
- `DATABASE_URL`: PostgreSQL connection string
- `LITERAL_API_KEY`: (Optional) For enhanced logging

## Code Architecture Notes

**Event Handling**: 
- Azure version: The `EventHandler` class in `app_azure.py` extends `AgentEventHandler` to stream Azure AI Agent responses in real-time to the Chainlit UI.
- Legacy version: The `EventHandler` class in `app.py` extends `AsyncAssistantEventHandler` for OpenAI Assistant streaming.

**File Processing**: 
- Azure version: File uploads are handled through Azure AI Projects file management APIs
- Legacy version: File uploads are processed through OpenAI's file API
- Both support code interpretation and file search capabilities

**Database Schema**: Prisma schema defines models for `Thread`, `Step`, `Element`, `User`, and `Feedback` to persist conversation history.

**Multi-stage Docker Build**: The Dockerfile uses a builder pattern to minimize final image size while installing all Python dependencies.

**Authentication**: Azure AI version uses `DefaultAzureCredential` for seamless authentication with Azure services.

## Key Integration Points

### Azure AI Version
- **Azure AI Projects**: Unified project management and model deployment
- **Azure AI Agents**: Agent creation, streaming, and tool execution
- **Chainlit Elements**: Dynamic rendering of plots, files, and images from Agent responses
- **Azure Authentication**: Seamless integration using DefaultAzureCredential
- **Database Logging**: All conversations are persisted via Prisma models

### Legacy OpenAI Version
- **OpenAI Assistant API**: Streaming responses with tool calls (code interpreter, file search)
- **Chainlit Elements**: Dynamic rendering of plots, files, and images from Assistant responses
- **File Processing**: File uploads processed through OpenAI's file API
- **Database Logging**: All conversations are persisted via Prisma models

## File Upload Support

The application supports various file types:
- **Code Interpretation**: CSV, JSON, Python files
- **File Search**: PDF, DOCX, Markdown, plain text files
- **Image Generation**: Assistant can generate and display plots using matplotlib/plotly

## Migration from OpenAI to Azure AI

This repository contains both the legacy OpenAI Assistant implementation and the new Azure AI Projects/Agents implementation:

**Files to use for Azure AI:**
- `src/app_azure.py`: Main application (replaces `app.py`)
- `src/create_agent_azure.py`: Agent creation (replaces `create_assistant.py`)
- `src/.env.template`: Environment variables template for Azure AI

**Key differences:**
- Uses `azure-ai-projects` and `azure-ai-agents` SDKs instead of `openai`
- Authentication via Azure DefaultAzureCredential instead of API keys
- Agent management through Azure AI Projects instead of direct OpenAI API calls
- Integrated with Azure model deployments and endpoints

## Deployment Notes

- Uses Azure Container Apps for serverless scaling
- Bicep templates in `infra/` provision all required Azure resources
- Environment variables are injected at deployment time
- Database migrations run automatically during deployment
- Azure AI version requires Azure AI Project setup and agent deployment