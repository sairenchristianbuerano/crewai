# CrewAI Component Generation Backend Services

> AI-powered tool component generation and indexing system for crewAI, inspired by Flowise architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/status-development-orange.svg)]()

## 📋 Overview

This project provides **two microservices** for generating and managing custom crewAI tool components:

1. **component-generator** - Generates crewAI `BaseTool` components from YAML specifications using Claude AI
2. **component-index** - Catalogs and indexes tools with semantic search capabilities (RAG-powered)

### Why This Project?

- **Accelerate Development:** Generate boilerplate crewAI tools in seconds instead of hours
- **Maintain Consistency:** Ensure all tools follow crewAI best practices
- **Enable Discovery:** Semantic search over existing tools to find and reuse components
- **Learn from Patterns:** RAG-based pattern matching helps generate better code

---

## 🎯 Key Features

### Tool Generator
- ✨ Generate complete crewAI `BaseTool` classes from simple YAML specs
- 🤖 Claude AI-powered code generation with validation
- 📝 5 built-in templates (API, Search, File, Database, Custom)
- ✅ Automatic validation and security checks
- 🔄 Auto-retry with fixes for common issues
- 🔍 RAG-based pattern matching for better code

### Tool Index
- 📚 Comprehensive tool registry with CRUD operations
- 🔎 Semantic search powered by ChromaDB
- 📊 Statistics and analytics dashboard
- 🏷️ Category-based organization
- 📈 Version and deployment tracking
- 🎯 Similar pattern discovery

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER/CLIENT LAYER                         │
│         (REST API clients, UI applications)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────────────┐   ┌─────────────────────┐
│  Tool Generator │   │    Tool Index       │
│    Service      │   │     Service         │
├─────────────────┤   ├─────────────────────┤
│ Port: 8085      │───│ Port: 8086          │
│                 │   │                     │
│ • Generate code │   │ • Registry (CRUD)   │
│ • Validate      │   │ • Pattern search    │
│ • Assess        │   │ • Statistics        │
│                 │   │                     │
│ FastAPI         │   │ FastAPI             │
│ Claude AI       │   │ ChromaDB            │
│ Jinja2          │   │ JSON Storage        │
└─────────────────┘   └─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Anthropic API Key (for Claude AI)
- Python 3.11+ (for local development)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd crewai

# Set your API key
export ANTHROPIC_API_KEY=your_anthropic_key_here

# Start both services
docker-compose up -d

# Check service health
curl http://localhost:8085/api/crewai/tool-generator/health
curl http://localhost:8086/api/crewai/tool-index/health
```

### Generate Your First Tool

```bash
# Create a YAML specification
cat > my_tool_spec.yaml <<EOF
name: WeatherTool
display_name: "Weather Lookup"
description: "Get weather information for a location"
category: api
platforms:
  - crewai

requirements:
  - "Accept location as input"
  - "Return temperature and conditions"

inputs:
  - name: location
    type: str
    description: "City name or zip code"
    required: true

dependencies:
  - "requests"

author: "Your Name"
version: "1.0.0"
EOF

# Generate the tool
curl -X POST http://localhost:8085/api/crewai/tool-generator/generate \
  -H "Content-Type: application/json" \
  -d "{\"spec\": \"$(cat my_tool_spec.yaml)\"}"
```

### Search for Existing Tools

```bash
# List all tools
curl http://localhost:8086/api/crewai/tools

# Search by category
curl "http://localhost:8086/api/crewai/tools?category=api"

# Semantic search for patterns
curl -X POST http://localhost:8086/api/crewai/patterns/search \
  -H "Content-Type: application/json" \
  -d '{"query": "tool that makes HTTP requests", "n_results": 5}'
```

---

## 📖 Documentation

- **[ROADMAP.md](ROADMAP.md)** - Project phases, todo list, and progress tracking
- **[API.md](API.md)** - Complete API reference (coming soon)
- **[component-generator/README.md](component-generator/README.md)** - Generator service documentation
- **[component-index/README.md](component-index/README.md)** - Index service documentation

---

## 📦 Project Structure

```
crewai/
├── README.md                         # This file
├── ROADMAP.md                        # Phases & progress tracking
├── docker-compose.yml                # Service orchestration
│
├── component-generator/              # Service 1: Generator
│   ├── src/
│   │   ├── service.py                # FastAPI app
│   │   ├── crewai_agent.py          # AI generator
│   │   ├── crewai_validator.py      # Validation
│   │   └── base_classes.py          # Models
│   ├── templates/                    # Jinja2 templates
│   ├── Dockerfile
│   └── requirements.txt
│
└── component-index/                  # Service 2: Index
    ├── src/
    │   ├── service.py                # FastAPI app
    │   ├── models.py                 # Data models
    │   ├── storage.py                # JSON storage
    │   └── crewai_rag_engine.py     # RAG search
    ├── data/                         # Storage
    │   ├── components/               # Registry
    │   ├── crewai_components/        # Knowledge base
    │   └── chromadb/                 # Vector DB
    ├── Dockerfile
    └── requirements.txt
```

---

## 🔧 Development

### Local Development Setup

```bash
# Generator service
cd component-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/service.py

# Index service (in another terminal)
cd component-index
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/service.py
```

### Running Tests

```bash
# Generator tests
cd component-generator
pytest tests/

# Index tests
cd component-index
pytest tests/
```

---

## 🌐 API Endpoints

### Tool Generator Service (Port 8085)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/crewai/tool-generator/generate` | Generate tool from YAML spec |
| `POST` | `/api/crewai/tool-generator/assess` | Assess feasibility before generation |
| `GET` | `/api/crewai/tool-generator/health` | Health check |

### Tool Index Service (Port 8086)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/crewai/tools/register` | Register new tool |
| `GET` | `/api/crewai/tools` | List all tools |
| `GET` | `/api/crewai/tools/{id}` | Get specific tool |
| `GET` | `/api/crewai/tools/name/{name}` | Get tool by name |
| `DELETE` | `/api/crewai/tools/{id}` | Delete tool |
| `GET` | `/api/crewai/tools/stats` | Get statistics |
| `POST` | `/api/crewai/patterns/search` | Semantic search |
| `POST` | `/api/crewai/patterns/similar` | Find similar patterns |

**Full API documentation:** [API.md](API.md) (OpenAPI/Swagger at `/docs` when running)

---

## 📊 Current Status

**Version:** 0.1.0 (Development)
**Phase:** Phase 1 - Foundation & Setup
**Progress:** See [ROADMAP.md](ROADMAP.md) for detailed progress tracking

### Completed
- ✅ Architecture design
- ✅ Feasibility assessment
- ✅ Documentation structure

### In Progress
- 🔄 Project setup
- 🔄 Service implementation

### Upcoming
- ⏸️ Testing & integration
- ⏸️ Deployment configuration

---

## 🛠️ Technology Stack

- **Framework:** FastAPI 0.104.1
- **AI Engine:** Anthropic Claude (Sonnet 4)
- **Templates:** Jinja2
- **Vector DB:** ChromaDB 0.4.x
- **Embeddings:** sentence-transformers
- **Storage:** JSON (with PostgreSQL option)
- **Containerization:** Docker & Docker Compose
- **Language:** Python 3.11+

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. (Coming soon)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [Flowise](https://github.com/FlowiseAI/Flowise) component generation architecture
- Built for the [crewAI](https://github.com/joaomdmoura/crewAI) framework
- Powered by [Anthropic Claude](https://www.anthropic.com/)

---

## 📞 Support

- **Documentation:** [ROADMAP.md](ROADMAP.md), [API.md](API.md)
- **Issues:** GitHub Issues (when repository is public)
- **Discussions:** GitHub Discussions (when repository is public)

---

## 🔮 Future Enhancements

- [ ] Web UI for tool management
- [ ] Tool marketplace/sharing
- [ ] GitHub integration for version control
- [ ] Batch generation support
- [ ] Tool composition (combining multiple tools)
- [ ] PostgreSQL backend option
- [ ] Tool testing framework
- [ ] CI/CD pipeline

---

**Made with ❤️ for the crewAI community**

**Last Updated:** 2025-12-10
