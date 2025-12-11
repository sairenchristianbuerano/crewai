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

## 🖥️ Quick Start - Standalone Mode (No Docker)

For users without Docker or for local development.

### Prerequisites

- Python 3.11+ (3.13 recommended)
- pip
- Anthropic API key

### 1. One-Time Setup

**Linux/Mac/Git Bash (Windows):**
```bash
# Run setup script to create virtual environments and install dependencies
./setup_standalone.sh
```

**Windows PowerShell:**
```powershell
# Run setup script
.\setup_standalone.ps1
```

This will:
- Create isolated virtual environments for both services
- Install all Python dependencies
- Pre-download required ML models
- Create data directories
- Generate `.env.standalone` configuration file

### 2. Configure Environment

Edit `.env.standalone` and add your API key:

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional (defaults shown)
CLAUDE_MODEL=claude-sonnet-4-20250514
PORT_INDEX=8086
PORT_GENERATOR=8085
COMPONENT_RAG_URL=http://localhost:8086
```

### 3. Start Services

**Linux/Mac/Git Bash (Windows):**
```bash
# Start both services together
./run_standalone.sh
```

**Windows PowerShell:**
```powershell
# Start both services
.\run_standalone.ps1
```

This will:
- Start component-index on port 8086
- Wait for component-index to become healthy
- Start component-generator on port 8085
- Display live logs from both services

Services will continue running until you press Ctrl+C.

### 4. Stop Services

**Linux/Mac/Git Bash (Windows):**
```bash
# In another terminal, or after pressing Ctrl+C
./stop_standalone.sh
```

**Windows PowerShell:**
```powershell
# Stop services
.\stop_standalone.ps1
```

### Standalone vs Docker Comparison

| Feature | Docker | Standalone |
|---------|--------|------------|
| **Setup** | Docker required | Python 3.11+ required |
| **Isolation** | Container-level | venv-level |
| **Startup Time** | ~30 seconds | ~20 seconds |
| **Memory Usage** | Higher (containers) | Lower (native) |
| **Best For** | Production, CI/CD | Local development, debugging |

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

### Standalone Mode

**Services won't start:**
```bash
# Check if virtual environments exist
ls component-index/venv
ls component-generator/venv

# If missing, run setup again
./setup_standalone.sh  # or .\setup_standalone.ps1 on Windows

# Check logs
tail -f component-index.log
tail -f component-generator.log
```

**Port conflicts:**
```bash
# Edit .env.standalone to use different ports
PORT_INDEX=9086
PORT_GENERATOR=9085
COMPONENT_RAG_URL=http://localhost:9086
```

**API key issues:**
```bash
# Verify API key is set
cat .env.standalone | grep ANTHROPIC_API_KEY

# Test API key with curl
export ANTHROPIC_API_KEY=your_key_here
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

**Process cleanup:**
```bash
# Clean up stale PID files if services crashed
rm .component-index.pid .component-generator.pid

# Kill orphaned Python processes (Linux/Mac)
pkill -f "python src/service.py"

# Kill orphaned Python processes (Windows PowerShell)
Get-Process python | Where-Object {$_.Path -like "*venv*"} | Stop-Process
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
