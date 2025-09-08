# GenAI Stack - No-Code Workflow Builder

<div align="center">

![GenAI Stack Logo](docs/images/genai-stack-logo.png)

**Build Intelligent AI Workflows Without Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

[Demo](https://genai-stack-demo.herokuapp.com) • [Documentation](docs/) • [API Docs](https://api.genai-stack.com/docs) • [Contributing](#contributing)

</div>

## 🎯 Overview

GenAI Stack is a powerful, visual workflow builder that enables anyone to create sophisticated AI-powered applications without writing code. Drag and drop components to build workflows that combine large language models, knowledge bases, web search, and custom logic.

### ✨ Key Features

- **🎨 Visual Workflow Builder**: Intuitive drag-and-drop interface
- **🤖 AI Integration**: OpenAI GPT, Google Gemini, and custom models
- **📚 Knowledge Base**: Upload and query documents with vector search
- **🔍 Web Search**: Real-time web search capabilities
- **💬 Chat Interface**: Test workflows through conversational UI
- **🔗 API-First**: REST APIs for all functionality
- **🚀 Production Ready**: Docker containerization and Kubernetes deployment
- **📊 Monitoring**: Built-in metrics and health checks

## 🏗️ Architecture
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ React Frontend │────│ FastAPI │────│ PostgreSQL │
│ TypeScript │ │ Python 3.9+ │ │ Database │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│
┌─────────┼─────────┐
│ │ │
┌───────▼───┐ ┌───▼───┐ ┌───▼────┐
│ ChromaDB │ │ Redis │ │ OpenAI │
│ Vector DB │ │ Cache │ │ API │
└───────────┘ └───────┘ └────────┘

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### 1. Clone Repository
git clone https://github.com/your-username/genai-stack.git
cd genai-stack

### 2. Environment Setup
cp .env.example .env

### 3. Start with Docker Compose
Development
docker-compose up -d

Production
docker-compose -f docker-compose.prod.yml up -d

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ❌ |
| `SERP_API_KEY` | SerpAPI key for web search | ❌ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `CHROMA_URL` | ChromaDB service URL | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |

## 🎮 Usage

### Building Your First Workflow

1. **Add Components**: Drag components from the library to the canvas
2. **Configure Nodes**: Click on nodes to configure settings
3. **Connect Components**: Link components to create data flow
4. **Test Workflow**: Use the chat interface to test your workflow
5. **Deploy**: Save and deploy your workflow

### Supported Components

- **User Query**: Entry point for user input
- **LLM Engine**: Large language model processing (OpenAI, Gemini)
- **Knowledge Base**: Document upload and vector search
- **Web Search**: Real-time web search integration
- **Output**: Format and return results

## 🛠️ Development

### Local Development Setup
Backend
cd backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend
cd frontend
npm install
npm start

### Running Tests
Backend tests
cd backend
pytest

Frontend tests
cd frontend
npm test

### Code Quality
Python linting
black backend/
flake8 backend/

TypeScript linting
cd frontend
npm run lint


## 📦 Deployment

### Docker Deployment
Build and deploy
make build
make deploy

Or use helper scripts
./scripts/build.sh
./scripts/deploy.sh

### Kubernetes Deployment
Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/

See [Deployment Guide](docs/deployment-guide.md) for detailed instructions.

## 📚 Documentation

- [🏗️ Architecture Overview](docs/architecture.md)
- [📖 API Documentation](docs/api-documentation.md)
- [⚙️ Setup Guide](docs/setup-guide.md)
- [🚀 Deployment Guide](docs/deployment-guide.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT models
- [Google AI](https://ai.google/) for Gemini models
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React Flow](https://reactflow.dev/) for the workflow canvas
- [ChromaDB](https://www.trychroma.com/) for vector storage

## 📞 Support

- 📧 Email: support@genai-stack.com
- 💬 Discord: [Join our community](https://discord.gg/genai-stack)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/genai-stack/issues)

---

<div align="center">
Made BY JOHAN THOMAS ISAAC
</div>



