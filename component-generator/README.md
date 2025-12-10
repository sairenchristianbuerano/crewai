# CrewAI Tool Generator Service

> AI-powered code generation service for crewAI custom tools

## 📋 Overview

This service generates production-ready crewAI `BaseTool` components from YAML specifications using Claude AI. It validates the generated code, provides feasibility assessments, and integrates with the Tool Index service for pattern-based learning.

## 🎯 Features

- ✨ Generate complete crewAI tool classes from simple YAML specs
- 🤖 Claude AI-powered code generation (Sonnet 4)
- ✅ Automatic Python syntax and structure validation
- 🔒 Security validation (forbidden imports, dangerous patterns)
- 🔄 Auto-retry with error fixes (up to 3 attempts)
- 🔍 RAG-based pattern matching from existing tools
- 📝 Automatic documentation generation
- ⚡ Feasibility assessment before generation

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│   Tool Generator Service             │
│   (Port 8085)                        │
├──────────────────────────────────────┤
│                                      │
│  ┌─────────────┐  ┌──────────────┐ │
│  │   FastAPI   │  │  Claude AI   │ │
│  │   Service   │  │  Generator   │ │
│  └──────┬──────┘  └──────┬───────┘ │
│         │                │          │
│         └────────┬───────┘          │
│                  │                  │
│      ┌───────────▼────────────┐    │
│      │   CrewAI Validator     │    │
│      └───────────┬────────────┘    │
│                  │                  │
│                  ▼                  │
│       Generated BaseTool Code       │
└──────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key

### Local Development

```bash
# Navigate to service directory
cd crewai-tool-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run service
python src/service.py
```

Service will start on `http://localhost:8085`

### With Docker

```bash
# From project root
docker-compose up -d tool-generator
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/crewai/tool-generator/health
```

### Generate Tool
```bash
POST /api/crewai/tool-generator/generate
Content-Type: application/json

{
  "spec": "<YAML specification>"
}
```

**Response:**
```json
{
  "code": "from crewai.tools import BaseTool...",
  "documentation": "# Tool Name\n...",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "suggestions": []
  },
  "dependencies": ["requests"],
  "deployment_instructions": {...}
}
```

### Assess Feasibility
```bash
POST /api/crewai/tool-generator/assess
Content-Type: application/json

{
  "spec": "<YAML specification>"
}
```

**Response:**
```json
{
  "feasible": true,
  "confidence": "high",
  "complexity": "medium",
  "issues": [],
  "suggestions": [],
  "missing_info": [],
  "similar_patterns_found": 3
}
```

## 📝 YAML Specification Format

```yaml
name: ToolName                # PascalCase class name
display_name: "Tool Display"  # Human-readable name
description: "What it does"   # Tool description
category: api                 # api, search, file, database, custom
platforms:
  - crewai

requirements:                 # Functional requirements
  - "Requirement 1"
  - "Requirement 2"

inputs:                       # Tool parameters
  - name: param1
    type: str
    description: "Parameter description"
    required: true

config_params:                # Optional __init__ parameters
  - name: config1
    type: "Optional[str]"
    description: "Config parameter"

dependencies:                 # Python packages
  - "requests"

author: "Your Name"
version: "1.0.0"
```

See [sample_spec.yaml](sample_spec.yaml) for a complete example.

## 🔧 Configuration

Environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Claude API key |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-20250514` | Model to use |
| `PORT` | No | `8085` | Service port |
| `RAG_SERVICE_URL` | No | `http://localhost:8086` | Tool Index service URL |
| `CORS_ORIGINS` | No | See code | Allowed CORS origins |

## 🧪 Testing

### Test Generation
```bash
curl -X POST http://localhost:8085/api/crewai/tool-generator/generate \
  -H "Content-Type: application/json" \
  -d "{\"spec\": \"$(cat sample_spec.yaml)\"}"
```

### Test Feasibility
```bash
curl -X POST http://localhost:8085/api/crewai/tool-generator/assess \
  -H "Content-Type: application/json" \
  -d "{\"spec\": \"name: TestTool\ndescription: Test tool\"}"
```

## 📊 Validation

The generator validates:

- ✅ Python syntax correctness
- ✅ BaseTool interface compliance
- ✅ Required attributes (`name`, `description`, `args_schema`)
- ✅ Required methods (`_run`, `run`)
- ✅ Input schema (Pydantic BaseModel)
- ✅ Security issues (forbidden imports, dangerous functions)
- ✅ Code structure and organization

## 🔒 Security

The validator checks for:

- ❌ Forbidden imports (`eval`, `exec`, `__import__`)
- ❌ Dangerous function calls
- ❌ Shell command execution without validation
- ✅ Proper input sanitization
- ✅ Type annotations
- ✅ Error handling

## 🛠️ Troubleshooting

### Claude API Errors
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# View logs
docker logs crewai-tool-generator -f
```

### Validation Failures

The generator auto-retries up to 3 times with error feedback. Check:
- YAML specification format
- Required fields present
- Dependencies valid

### RAG Service Unavailable

RAG integration is optional. Service works without it but with reduced pattern matching.

## 📚 Related Files

- [base_classes.py](src/base_classes.py) - Data models and interfaces
- [crewai_agent.py](src/crewai_agent.py) - Claude AI generator
- [crewai_validator.py](src/crewai_validator.py) - Validation logic
- [service.py](src/service.py) - FastAPI application

## 🆘 Support

- **Logs:** `docker logs crewai-tool-generator -f`
- **Health:** `http://localhost:8085/api/crewai/tool-generator/health`
- **Docs:** `http://localhost:8085/docs` (Swagger UI)

---

**Service:** crewai-tool-generator
**Port:** 8085
**Version:** 0.1.0
