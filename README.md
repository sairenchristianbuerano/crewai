# CrewAI Component Generator & Index

Backend services for generating and managing custom CrewAI components.

**CrewAI Version:** Component generator targets [CrewAI v0.86.0](https://github.com/joaomdmoura/crewAI) tool architecture

📖 **[API Documentation](API.md)** - Complete endpoint reference

---

## 📋 Overview

This repository contains two microservices specifically for CrewAI platform:

1. **Component Generator** (Port 8085) - Generates custom CrewAI component code from YAML specifications using Claude AI
2. **Component Index** (Port 8086) - Tracks and manages generated components with semantic pattern search (RAG)

The Component Index provides both component registry functionality and semantic search over CrewAI component patterns to help generate better, more consistent code.

---

## 🏗️ Architecture

```
crewai/
├── component-generator/      # Code generation service (Port 8085)
│   ├── src/
│   │   ├── service.py        # FastAPI endpoints
│   │   ├── crewai_agent.py   # Core generator with Claude AI
│   │   └── crewai_validator.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── component-index/          # Component registry & RAG (Port 8086)
│   ├── src/
│   │   ├── service.py        # FastAPI endpoints
│   │   ├── storage.py        # JSON-based component registry
│   │   └── crewai_rag_engine.py  # Pattern search engine
│   ├── data/
│   │   └── crewai_components/   # Component knowledge base
│   ├── Dockerfile
│   └── requirements.txt
│
└── docker-compose.yml        # Service orchestration
```

---

## 🚀 Quick Start - Docker

### Prerequisites

- Docker & Docker Compose
- Anthropic API key (for Claude)

### 1. Set Environment Variables

Create a `.env` file:

```bash
# Required: Claude API key for code generation
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Claude model selection (default shown)
CLAUDE_MODEL=claude-sonnet-4-20250514

# Optional: Pattern search URL (served by component-index)
COMPONENT_RAG_URL=http://component-index:8086
```

### 2. Start Services

```bash
# Build and start both services
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify services are healthy
curl http://localhost:8085/api/crewai/component-generator/health
curl http://localhost:8086/api/crewai/component-index/health
```

### 3. Stop Services

```bash
docker-compose down
```

---

## 📡 API Endpoints

Both services provide REST APIs for component generation and management.

📖 **See [API.md](API.md) for complete endpoint documentation** including:
- Component Generator API (health, generate, assess feasibility)
- Component Index API (register, list, search, CRUD operations)
- Pattern Search API (semantic search over component patterns)
- YAML specification format
- Request/response examples
- Error handling

### Quick Examples

**Generate a Component:**
```bash
curl -X POST http://localhost:8085/api/crewai/component-generator/generate \
  -H "Content-Type: application/json" \
  -d '{"spec": "name: CalculatorTool\ndisplay_name: Calculator\ndescription: Perform calculations\ncategory: tools\nplatforms:\n  - crewai\nrequirements:\n  - Evaluate math expressions"}'
```

**List Components:**
```bash
curl http://localhost:8086/api/crewai/component-index/components
```

**Search for Patterns:**
```bash
curl -X POST http://localhost:8086/api/crewai/component-index/patterns/search \
  -H "Content-Type: application/json" \
  -d '{"query": "text processing tool", "n_results": 3}'
```

---

## 🧪 Testing

An automated test script validates all service endpoints:

```bash
python test_all_endpoints.py
```

**What Gets Tested:**
- ✅ Component Generator health check
- ✅ Sample component generation (uses cached sample)
- ✅ Component Index health & statistics
- ✅ Component registry CRUD operations
- ✅ Pattern search functionality
- ✅ CORS headers validation

---

## 🛠️ Troubleshooting

### Docker Mode

**Services won't start:**
```bash
# Check logs
docker-compose logs -f

# Verify .env file has ANTHROPIC_API_KEY
cat .env | grep ANTHROPIC_API_KEY
```

**Port conflicts:**
```bash
# Change ports in docker-compose.yml if needed
ports:
  - "9085:8085"  # Use port 9085 instead
  - "9086:8086"  # Use port 9086 instead
```

**View logs:**
```bash
# Component Index logs
docker-compose logs component-index

# Component Generator logs
docker-compose logs component-generator
```

---

## 📚 Related Documentation

### Service Documentation
- [API.md](API.md) - Complete API reference with endpoint details for both services

### External Resources
- [CrewAI Documentation](https://docs.crewai.com) - Official CrewAI docs
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI) - Main framework repository

---

## 🆘 Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Verify health endpoints: `curl http://localhost:8085/health` and `curl http://localhost:8086/health`
3. Ensure API keys are set correctly in `.env`
4. Review [API.md](API.md) for YAML specification format

---

## 📄 License

MIT
