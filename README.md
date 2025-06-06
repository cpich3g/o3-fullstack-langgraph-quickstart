# Azure AI Deep Research Agent

A sophisticated fullstack application powered by **Azure AI** models and LangGraph for intelligent web research. This research assistant performs comprehensive analysis on user queries by dynamically generating search terms, conducting web research, reflecting on results to identify knowledge gaps, and iteratively refining its approach to deliver well-supported answers with citations.

![Azure AI Deep Research Agent](./app.png)

## Features

- 💬 **Modern Fullstack Architecture** - React frontend with TypeScript and LangGraph-powered backend
- 🤖 **Azure AI Integration** - Powered by Azure OpenAI's latest models for superior reasoning
- 🔍 **Intelligent Research** - Dynamic search query generation and iterative refinement
- 🌐 **Web Research Engine** - Integrated Tavily Search API with smart content analysis
- 🧠 **Reflective AI** - Self-analyzing system that identifies knowledge gaps and adapts strategies
- 📚 **Source Citations** - Comprehensive answers with proper attribution and references
- ⚡ **Real-time Updates** - Live progress tracking with activity timeline
- 🎨 **Modern UI** - Clean, responsive interface with dark theme and sidebar layout

## Project Structure

```
📦 o3-fullstack-langgraph-quickstart/
├── 🎨 frontend/          # React + TypeScript + Tailwind CSS
│   ├── src/components/   # UI components with modern design
│   └── ...
├── 🤖 backend/           # LangGraph + FastAPI + Azure AI
│   ├── src/agent/       # Research agent logic
│   │   ├── graph.py     # LangGraph workflow
│   │   ├── configuration.py  # model configuration
│   │   └── tools.py     # Web research tools
└── 🐳 Deployment files  # Docker & docker-compose
```

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Azure OpenAI API Key** with access to latest models
- **Tavily Search API Key** for web research (optional)

### Environment Setup

1. **Configure Azure OpenAI credentials:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Add your Azure OpenAI credentials to `.env`:**
   ```env
   AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
   AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   AZURE_OPENAI_API_VERSION="2024-12-01-preview"
   TAVILY_API_KEY="your_tavily_api_key"  # Optional for web research
   ```

### Installation & Development

1. **Install backend dependencies:**
   ```bash
   cd backend
   pip install .
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Start development servers:**
   ```bash
   make dev
   ```

4. **Access the application:**
   - Frontend: `http://localhost:5173/app`
   - Backend API: `http://localhost:2024`
   - LangGraph UI: `http://localhost:2024/docs`

## How It Works

The research assistant uses a sophisticated multi-step approach powered by Azure AI models:

![Agent Research Flow](./agent.png)

### 🎯 **Intelligent Query Planning**
- **Azure AI** analyzes user input and generates strategic search queries
- Advanced prompt engineering ensures comprehensive coverage of topics

### 🔍 **Adaptive Web Research**
- Executes targeted web searches using Tavily Search API
- **Azure AI** processes and analyzes search results for relevance and quality
- Extracts key information while maintaining source attribution

### 🧠 **Reflective Analysis**
- **Azure AI's reasoning capabilities** identify knowledge gaps and inconsistencies
- Determines if additional research is needed or if information is sufficient
- Self-correcting mechanism improves research quality iteratively

### 🔄 **Iterative Refinement**
- Generates follow-up queries based on gap analysis
- Continues research until comprehensive understanding is achieved
- Configurable loop limits prevent infinite iterations

### 📝 **Synthesis & Response**
- **Azure AI** synthesizes gathered information into coherent, well-structured answers
- Includes proper citations and source references
- Maintains factual accuracy while ensuring readability

## Production Deployment

The application is production-ready with Docker support and requires Redis and PostgreSQL for LangGraph operations.

### Prerequisites
- **Docker & Docker Compose** - For containerized deployment
- **Redis** - Message broker for real-time streaming
- **PostgreSQL** - Data persistence and state management
- **Azure OpenAI** - latest model access

### Docker Deployment

1. **Build the production containers:**
   ```bash
   docker-compose -f docker-compose.production.yml build --no-cache
   ```

2. **Configure environment variables:**
   ```bash
   # Copy and update with your Azure OpenAI credentials
   cp .env.example .env
   ```

3. **Deploy with docker-compose:**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

4. **Access the application:**
   - Application: `http://localhost:8000/app/`
   - API: `http://localhost:8000`

### Environment Configuration

Update `frontend/src/App.tsx` with your deployment URL:
- **Development:** `http://localhost:2024`
- **Docker:** `http://localhost:8000`
- **Production:** Your domain/IP address

## Model Configuration

The application uses specific Azure AI models configurations defined in `backend/src/agent/configuration.py`:

```python
# Default Azure AI model configuration
query_generator_model: str = "gpt-4.1-mini"    # Search query generation
reflection_model: str = "o4-mini"              # Research gap analysis
answer_model: str = "gpt-4.1-mini"             # Final response synthesis
reasoning_model: str = "o4-mini"               # Iterative reasoning
```

**Azure OpenAI Deployment Setup:**
1. Deploy the required Azure AI models in your Azure OpenAI resource
2. Use the deployment names that match the configuration above
3. Ensure your API version supports Azure AI models: `2024-12-01-preview`

## Technology Stack

### Frontend
- **[React](https://reactjs.org/)** with **[TypeScript](https://www.typescriptlang.org/)** - Type-safe component architecture
- **[Vite](https://vitejs.dev/)** - Fast development and optimized builds
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first styling framework
- **[Shadcn UI](https://ui.shadcn.com/)** - Modern, accessible component library

### Backend
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Advanced agent workflow orchestration
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python web framework
- **[Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)** - O3-mini models for reasoning and generation
- **[Tavily](https://tavily.com/)** - Web search and research API

### Infrastructure
- **[Docker](https://www.docker.com/)** - Containerized deployment
- **[Redis](https://redis.io/)** - Real-time message streaming
- **[PostgreSQL](https://www.postgresql.org/)** - Persistent data storage

## Azure OpenAI Models

This application leverages Azure AI's latest models for enhanced reasoning:

### 🚀 **Azure AI Models Configuration**
- **Query Generation**: `gpt-4.1-mini` - Strategic search query formulation
- **Reflection & Reasoning**: `o4-mini` - Advanced analytical capabilities and gap identification  
- **Answer Synthesis**: `gpt-4.1-mini` - Coherent response generation with citations

### 🧠 **Azure AI Capabilities**
- **Advanced Reasoning** - Superior logical analysis and problem-solving
- **Context Awareness** - Maintains coherent analysis across complex research topics
- **Self-Reflection** - Meta-cognitive abilities for iterative research improvement
- **Efficient Processing** - Optimized performance for real-time research workflows

## Key Benefits

✅ **Latest AI Technology** - Built with Azure OpenAI's cutting-edge models  
✅ **Advanced Reasoning** - State-of-the-art analytical and reflection capabilities  
✅ **Real-Time Research** - Live web data integration with smart content analysis  
✅ **Accurate Citations** - Proper source attribution and fact verification  
✅ **Production Ready** - Docker deployment with Redis and PostgreSQL support  
✅ **Modern UI/UX** - Intuitive interface with real-time progress tracking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Documentation

- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - Agent workflow framework
- **[Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)** - AI model documentation
- **[LangSmith](https://smith.langchain.com/)** - Monitoring and observability platform

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details. 