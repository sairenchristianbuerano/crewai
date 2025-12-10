# CrewAI Tool Index Service

> Tool registry and semantic search service for crewAI components

## 📋 Overview

This service provides a comprehensive registry for crewAI tools with semantic search capabilities. It indexes tool metadata, enables discovery through pattern matching using RAG (ChromaDB), and provides statistics and analytics.

## 🎯 Features

- 📚 Complete tool registry with CRUD operations
- 🔍 Semantic search powered by ChromaDB
- 📊 Statistics and analytics dashboard
- 🏷️ Category-based organization
- 📈 Version and deployment tracking
- 🎯 Similar pattern discovery (RAG)
- 💾 JSON-based storage (PostgreSQL option available)

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│   Tool Index Service                 │
│   (Port 8086)                        │
├──────────────────────────────────────┤
│                                      │
│  ┌─────────────┐  ┌──────────────┐ │
│  │   FastAPI   │  │   ChromaDB   │ │
│  │   Service   │  │   RAG Engine │ │
│  └──────┬──────┘  └──────┬───────┘ │
│         │                │          │
│    ┌────▼────────────────▼─────┐   │
│    │   JSON Storage Layer      │   │
│    └───────────────────────────┘   │
│                                      │
│    Tool Registry + Pattern Search    │
└──────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- CrewAI-Studio tools (optional, for pattern matching)

### Local Development

```bash
# Navigate to service directory
cd crewai-tool-index

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run service
python src/service.py
```

Service will start on `http://localhost:8086`

### With Docker

```bash
# From project root
docker-compose up -d tool-index
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/crewai/tool-index/health
```

### Tool Registry Endpoints

#### Register Tool
```bash
POST /api/crewai/tools/register
Content-Type: application/json

{
  "name": "CustomApiTool",
  "display_name": "API Caller",
  "description": "Make HTTP API calls",
  "category": "api",
  "platform": "crewai",
  "version": "1.0.0",
  "author": "Author Name",
  "code_size": 2048,
  "dependencies": ["requests"],
  "validation_passed": true
}
```

#### List Tools
```bash
GET /api/crewai/tools?category=api&limit=10&offset=0
```

#### Get Tool by ID
```bash
GET /api/crewai/tools/{tool_id}
```

#### Get Tool by Name
```bash
GET /api/crewai/tools/name/CustomApiTool
```

#### Update Deployment Status
```bash
PATCH /api/crewai/tools/{tool_id}/deployment?status=deployed
```

#### Delete Tool
```bash
DELETE /api/crewai/tools/{tool_id}
```

#### Get Statistics
```bash
GET /api/crewai/tools/stats
```

### Pattern Search Endpoints (RAG)

#### Semantic Search
```bash
POST /api/crewai/patterns/search
Content-Type: application/json

{
  "query": "tool that makes HTTP requests",
  "n_results": 5,
  "category": "api"
}
```

#### Find Similar Patterns
```bash
POST /api/crewai/patterns/similar
Content-Type: application/json

{
  "description": "A tool that searches the web",
  "category": "search",
  "n_results": 3
}
```

#### Reindex Patterns
```bash
POST /api/crewai/patterns/index
Content-Type: application/json

{
  "force_reindex": false
}
```

#### Get Pattern Statistics
```bash
GET /api/crewai/patterns/stats
```

#### Get Pattern by Name
```bash
GET /api/crewai/patterns/{pattern_name}
```

## 💾 Data Storage

### Tool Registry
Stored in JSON format at `/app/data/components/index.json`:

```json
{
  "tool-uuid-1": {
    "tool_id": "tool-uuid-1",
    "name": "CustomApiTool",
    "display_name": "API Caller",
    "description": "Make HTTP API calls",
    "category": "api",
    "platform": "crewai",
    "version": "1.0.0",
    "created_at": "2025-12-10T10:00:00Z",
    "updated_at": "2025-12-10T10:00:00Z",
    "author": "User",
    "status": "generated",
    "code_size": 2048,
    "dependencies": ["requests"],
    "validation_passed": true,
    "deployment_status": null
  }
}
```

### Pattern Knowledge Base
- **Directory:** `/app/data/tools` (read-only)
- **Format:** Python files with crewAI BaseTool classes
- **Indexed in:** ChromaDB at `/app/data/chromadb`

## 🔧 Configuration

Environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `8086` | Service port |
| `STORAGE_PATH` | No | `/app/data/components` | Registry storage path |
| `TOOLS_DIR` | No | `/app/data/tools` | Pattern knowledge base |
| `CHROMADB_DIR` | No | `/app/data/chromadb` | ChromaDB storage |
| `CORS_ORIGINS` | No | See code | Allowed CORS origins |

## 🧪 Testing

### Register a Tool
```bash
curl -X POST http://localhost:8086/api/crewai/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestTool",
    "display_name": "Test Tool",
    "description": "Test tool for demo",
    "category": "custom",
    "platform": "crewai",
    "author": "Test User",
    "code_size": 1024,
    "validation_passed": true
  }'
```

### List All Tools
```bash
curl http://localhost:8086/api/crewai/tools
```

### Search Patterns
```bash
curl -X POST http://localhost:8086/api/crewai/patterns/search \
  -H "Content-Type: application/json" \
  -d '{"query": "API tool", "n_results": 5}'
```

### Get Statistics
```bash
curl http://localhost:8086/api/crewai/tools/stats
```

## 🔍 Pattern Search (RAG)

The RAG engine indexes existing tools for semantic search:

1. **Indexing:** On startup, scans `/app/data/tools` for Python files
2. **Embedding:** Uses `sentence-transformers` (all-MiniLM-L6-v2)
3. **Storage:** Vector embeddings stored in ChromaDB
4. **Search:** Semantic similarity search over tool code and metadata

### Supported Patterns

The engine automatically detects:
- API tools (`requests`, `http` patterns)
- Search tools (`search`, `ddg` patterns)
- File tools (`file`, `write` patterns)
- Database tools (`database`, `sql` patterns)

## 📊 Statistics

The service provides comprehensive statistics:

```json
{
  "total_tools": 15,
  "by_platform": {
    "crewai": 15
  },
  "by_category": {
    "api": 5,
    "search": 3,
    "file": 4,
    "custom": 3
  },
  "by_status": {
    "generated": 12,
    "deployed": 3
  },
  "total_code_size": 30720
}
```

## 🛠️ Troubleshooting

### Storage Errors
```bash
# Check storage directory
docker exec crewai-tool-index ls -la /app/data/components/

# View index file
docker exec crewai-tool-index cat /app/data/components/index.json
```

### ChromaDB Issues
```bash
# Check ChromaDB directory
docker exec crewai-tool-index ls -la /app/data/chromadb/

# Reindex patterns
curl -X POST http://localhost:8086/api/crewai/patterns/index \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": true}'
```

### No Patterns Found

Ensure tools are mounted correctly:
1. Check `CREWAI_STUDIO_TOOLS_PATH` in `.env`
2. Verify tools exist in `/app/data/tools`
3. Reindex using the `/patterns/index` endpoint

## 📚 Related Files

- [models.py](src/models.py) - Data models
- [storage.py](src/storage.py) - JSON storage layer
- [crewai_rag_engine.py](src/crewai_rag_engine.py) - RAG engine
- [service.py](src/service.py) - FastAPI application

## 🆘 Support

- **Logs:** `docker logs crewai-tool-index -f`
- **Health:** `http://localhost:8086/api/crewai/tool-index/health`
- **Docs:** `http://localhost:8086/docs` (Swagger UI)

---

**Service:** crewai-tool-index
**Port:** 8086
**Version:** 0.1.0
