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
- 🎨 **Enhanced Professional UI** - Clean, responsive widescreen desktop interface with modern design
- 🎯 **Research Intelligence Panel** - AI-powered insights with methodology analysis, source quality tracking, and progress monitoring
- 📊 **Visualization Carousel** - Interactive carousel for generated charts and data visualizations with keyboard navigation
- 🚀 **Quick Research Templates** - Industry-specific research prompts for Retail, Manufacturing, Hospitality, and more
- 🔄 **Smart Collapsible Interface** - Adaptive sidebar that optimizes space based on usage context
- 📈 **Dynamic Progress Tracking** - Real-time research progress with intelligent confidence scoring

## Project Structure

```
📦 o3-fullstack-langgraph-quickstart/
├── 🎨 frontend/          # React + TypeScript + Tailwind CSS
│   ├── src/components/   # Enhanced UI components
│   │   ├── VisualizationCarousel.tsx    # Interactive visualization display
│   │   ├── ChatMessagesView.tsx         # Enhanced chat interface
│   │   ├── ActivityTimeline.tsx         # Research progress tracking
│   │   ├── ThemeProvider.tsx           # Dark theme management
│   │   ├── WelcomeScreen.tsx           # Improved welcome interface
│   │   └── ui/                         # Shadcn UI components
│   ├── src/lib/         # Utilities and helpers
│   └── ...
├── 🤖 backend/           # LangGraph + FastAPI + Azure AI
│   ├── src/agent/       # Research agent logic
│   │   ├── graph.py     # LangGraph workflow
│   │   ├── configuration.py  # Model configuration
│   │   ├── tools_and_schemas.py  # Web research tools
│   │   ├── prompts.py   # AI prompts and templates
│   │   └── state.py     # Agent state management
├── 📝 Documentation/    # Enhanced documentation
│   ├── UI_ENHANCEMENT_SUMMARY.md
│   ├── RESEARCH_INTELLIGENCE_FIXES.md
│   └── LAYOUT_IMPROVEMENTS_SUMMARY.md
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

### 🎨 UI Features Overview

Once running, you'll experience:
- **Research Intelligence Panel** - Real-time insights with color-coded analysis cards
- **Quick Research Templates** - Industry-specific prompts for immediate use
- **Interactive Progress Tracking** - Visual progress ring with research mode indicators
- **Visualization Carousel** - Modern display for generated charts and data
- **Smart Collapsible Layout** - Interface adapts to optimize space during research

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
- **[Lucide React](https://lucide.dev/)** - Beautiful icon library for modern interfaces
- **[React Markdown](https://github.com/remarkjs/react-markdown)** - Advanced markdown rendering with GFM support

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
✅ **Professional UI/UX** - Widescreen-optimized interface with research intelligence panel  
✅ **Smart Insights** - AI-powered methodology analysis and progress tracking  
✅ **Interactive Visualizations** - Modern carousel with keyboard navigation support  
✅ **Industry Templates** - Pre-configured research prompts for business use cases  
✅ **Adaptive Layout** - Collapsible interface that optimizes space intelligently  
✅ **Overflow Protection** - Responsive design with proper text wrapping and layout management

## 🔄 Recent Updates & Improvements

### UI/UX Enhancement (v2.0)
**Professional Widescreen Experience**
- ✅ **Research Intelligence Panel** - Comprehensive insights with methodology analysis, source tracking, and progress monitoring
- ✅ **Visualization Carousel** - Interactive carousel for charts with keyboard navigation and dot indicators
- ✅ **Smart Collapsible Layout** - Quick research section automatically collapses during active conversations
- ✅ **Industry-Specific Templates** - Added Retail, Manufacturing, and Hospitality research prompts
- ✅ **Overflow Protection** - Fixed text wrapping and responsive layout issues
- ✅ **Unique Timestamps** - Each insight now shows realistic timing progression
- ✅ **Dynamic Confidence** - Real-time confidence calculations based on research quality
- ✅ **Optimized Metadata** - Streamlined to focus on Sources and timing information

### Component Architecture
- ✅ **VisualizationCarousel.tsx** - New carousel component for interactive data visualization display
- ✅ **Enhanced App.tsx** - Improved sidebar layout with collapsible sections and research intelligence
- ✅ **Responsive Design** - Better handling of different screen sizes and content overflow
- ✅ **Type Safety** - Enhanced TypeScript interfaces for research insights and metadata

### Performance Optimizations
- ✅ **Reduced Bundle Size** - Optimized component imports and removed unused dependencies
- ✅ **Smooth Animations** - 300ms transitions for collapsible sections and state changes
- ✅ **Efficient Rendering** - Improved React hooks and state management for better performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Documentation

- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - Agent workflow framework
- **[Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)** - AI model documentation
- **[LangSmith](https://smith.langchain.com/)** - Monitoring and observability platform

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 🎨 Enhanced UI/UX Features

The application features a comprehensive redesign optimized for professional widescreen desktop use with advanced research intelligence capabilities.

### 🔍 **Research Intelligence Panel**
- **Methodology Insights** - Real-time analysis of research strategy optimization and query generation
- **Source Quality Tracking** - Dynamic evaluation of source discovery, verification, and content analysis
- **Progress Analytics** - Intelligent tracking with confidence scoring based on research depth
- **Knowledge Gap Analysis** - Automated identification of information gaps with targeted follow-up strategies
- **Color-coded Cards** - Visual hierarchy with type-specific themes (Analysis: Blue, Sources: Green, Methodology: Purple, Progress: Orange)
- **Smart Timestamps** - Unique time tracking for each insight showing realistic research progression
- **Dynamic Confidence** - Real-time confidence calculations based on source count and research quality

### 📊 **Interactive Visualization Carousel**
- **Modern Carousel Design** - Sleek navigation for generated charts and data visualizations
- **Multi-Navigation Support** - Button controls, dot indicators, and keyboard arrow key navigation
- **Responsive Display** - Automatic sizing with backdrop blur effects for professional presentation
- **Progress Indicators** - Clear "X of Y" counters and visual navigation aids

### 🚀 **Industry-Specific Quick Research**
Pre-configured research templates for professional use cases:
- **🛍️ Retail Intelligence** - Consumer behavior trends, e-commerce patterns, omnichannel strategies
- **🏭 Manufacturing** - Industry 4.0 technologies, automation, supply chain optimization
- **🏨 Hospitality** - Guest experience innovations, recovery trends, technology adoption
- **🤖 AI Trends** - Latest developments in artificial intelligence and machine learning
- **📈 Crypto Market** - Blockchain adoption, DeFi analysis, market trends
- **🌱 Clean Energy** - Sustainability initiatives, renewable technology developments
- **💼 Future of Work** - Remote work impact, productivity trends, company culture

### 🔄 **Smart Adaptive Layout**
- **Collapsible Quick Research** - Automatically minimizes when research begins to optimize screen space
- **Manual Toggle Control** - Click-to-expand functionality with visual chevron indicators
- **Responsive Space Management** - Dynamic sidebar layout that adapts to content and usage context
- **Overflow Protection** - Proper text wrapping and responsive handling prevents layout breaks
- **Professional Spacing** - Consistent margins, padding, and gap management throughout

### 🎯 **Enhanced User Experience**
- **Real-time Progress Ring** - Visual progress indicator with percentage completion
- **Research Mode Labels** - Clear indication of research depth (Quick, Balanced, Thorough)
- **Status Indicators** - Color-coded status badges (Completed, In Progress, Pending)
- **Theme Integration** - Consistent dark theme with gradient backgrounds and backdrop blur
- **Optimized Typography** - Clear hierarchy with proper font weights and color contrast