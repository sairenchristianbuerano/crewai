# CrewAI Components Directory

This directory contains all CrewAI component source files for the RAG-powered component generator.

## 📁 Directory Structure

```
component-index/data/
├── crewai_components/          # ✅ COMMITTED TO GIT
│   ├── official/               # Official CrewAI tools (60+ tools)
│   │   ├── ai_mind_tool/
│   │   ├── apify_actors_tool/
│   │   ├── brave_search_tool/
│   │   └── ... (90+ official tools)
│   └── studio/                 # CrewAI Studio custom tools
│       ├── CSVSearchToolEnhanced.py
│       ├── CustomApiTool.py
│       ├── DuckDuckGoSearchTool.py
│       └── ... (7 custom tools)
├── chromadb/                   # ❌ GITIGNORED (regeneratable)
├── components/                 # ❌ GITIGNORED (runtime registry)
├── crewai_studio_components/   # ⚠️  DEPRECATED (migrated to unified)
├── official_crewai_tools/      # ⚠️  DEPRECATED (migrated to unified)
└── README.md                   # This file
```

## 🎯 What Gets Committed to Git

### ✅ Committed Files
- **crewai_components/**: Source code for all components
  - `official/`: 90+ official CrewAI tools from crewai-tools package (v1.5.0)
  - `studio/`: 7 custom tools created with CrewAI Studio

### ❌ Gitignored Files
- **chromadb/**: ChromaDB vector database files (binary, regeneratable)
- **components/**: Runtime component registry (generated at runtime)
- **crewai_studio_components/**: Old directory (deprecated)
- **official_crewai_tools/**: Old directory (deprecated)

## 🚀 Quick Start

### Initial Setup

Run the setup script to initialize everything:

```bash
# Install dependencies (if needed)
pip install -r requirements.txt

# Run setup script (initializes ChromaDB from components)
python setup.py
```

The setup script will:
1. Clean up old ChromaDB files (if needed)
2. Build and start Docker services
3. Wait for services to be healthy
4. Index all components from `crewai_components/`
5. Verify the setup

### Manual Setup (Alternative)

```bash
# 1. Start services
docker-compose up -d --build

# 2. Wait for services to be ready
sleep 30

# 3. Trigger component indexing
curl -X POST http://localhost:8086/api/crewai/component-index/patterns/index \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": true}'

# 4. Check status
curl http://localhost:8086/api/crewai/component-index/health
```

## 📊 Current Statistics

- **Official Tools:** 90+ tools from crewai-tools package (v1.5.0)
- **Studio Tools:** 7 custom CrewAI Studio tools
- **Total Indexed:** 97 tools in ChromaDB
- **Categories:** API, Search, File, Database, AI/ML, Web Scraping, and more
- **RAG Engine:** ChromaDB with semantic search

## 🔧 RAG Engine Configuration

The RAG engine is configured to:
- **Index from**: `/app/data/crewai_components` (scans both `official/` and `studio/`)
- **Persist to**: `/app/data/chromadb`
- **Scan mode**: Recursive (uses `rglob("*.py")`)

### How It Works

1. **Startup**: Service initializes and checks for existing ChromaDB
2. **Indexing**: Recursively scans `crewai_components/official/` and `crewai_components/studio/`
3. **Embeddings**: Creates vector embeddings for each tool using ChromaDB
4. **Search**: Provides semantic search over all indexed components

## 📖 API Endpoints

### Pattern Search

**POST** `/api/crewai/component-index/patterns/search`
```json
{
  "query": "web scraping tool",
  "n_results": 5,
  "category": "api"
}
```

**POST** `/api/crewai/component-index/patterns/similar`
```json
{
  "description": "A tool for extracting data from websites",
  "n_results": 3
}
```

**POST** `/api/crewai/component-index/patterns/index`
```json
{
  "force_reindex": true
}
```

**GET** `/api/crewai/component-index/patterns/stats`

**GET** `/api/crewai/component-index/patterns/{pattern_name}`

### Health Check

**GET** `/api/crewai/component-index/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "crewai-component-index",
  "version": "0.1.0",
  "pattern_engine": {
    "total_tools": 97,
    "has_embeddings": true
  }
}
```

## 🎨 Adding Custom Components

To add custom tools to the index:

1. **Add tool files** to `crewai_components/studio/`
   ```bash
   # Copy your tool file
   cp my_custom_tool.py component-index/data/crewai_components/studio/
   ```

2. **Reindex components**
   ```bash
   curl -X POST http://localhost:8086/api/crewai/component-index/patterns/index \
     -H "Content-Type: application/json" \
     -d '{"force_reindex": true}'
   ```

3. **Verify indexing**
   ```bash
   curl http://localhost:8086/api/crewai/component-index/patterns/stats
   ```

## 🔄 Updating Components

### Update Official Tools

To update official tools from the latest crewai-tools package:

```bash
# Copy latest tools from your crewai-tools installation
cp -r /path/to/crewai-tools/src/crewai_tools/tools/* \
  component-index/data/crewai_components/official/

# Reindex
python setup.py --force-reindex
```

### Update Custom Tools

Simply edit files in `crewai_components/studio/` and reindex.

## 🗄️ ChromaDB Storage Strategy

### Why ChromaDB is Gitignored

ChromaDB files are **NOT** committed to git because:

1. **Size**: 50-200+ MB of binary files bloats the repository
2. **Not Portable**: Binary files may not work across different OS/architectures
3. **Regeneratable**: Can be rebuilt from component source files in ~30 seconds
4. **Binary Diffs**: Git can't efficiently track changes in binary files

### The Right Approach

✅ **Commit**: Component source files (`crewai_components/`)
❌ **Gitignore**: ChromaDB binaries (`chromadb/`)
🔄 **Setup Script**: One-command initialization (`setup.py`)

This ensures:
- Clean repository
- Fast clones
- Always works (regenerated for each environment)
- Easy updates

## 🔍 Troubleshooting

### ChromaDB Not Indexing

```bash
# Check logs
docker-compose logs component-index

# Force reindex
curl -X POST http://localhost:8086/api/crewai/component-index/patterns/index \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": true}'
```

### Service Not Starting

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f component-index

# Restart services
docker-compose restart
```

### RAG Returning 0 Results

1. Check pattern stats to verify indexing
2. Ensure ChromaDB directory has files
3. Try force reindexing
4. Check component-index logs for errors

## 📝 Best Practices

1. **Always commit** component source files to git
2. **Never commit** ChromaDB binary files
3. **Use setup script** for clean initialization
4. **Reindex after** adding/updating components
5. **Test RAG** after major changes

## 🐳 Docker Configuration

The Docker setup mounts the entire data directory:

```yaml
volumes:
  - ./component-index/data:/app/data
```

Environment variables:
```yaml
- TOOLS_DIR=/app/data/crewai_components
- CHROMADB_DIR=/app/data/chromadb
```

## 🎓 Learn More

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI Tools Package](https://github.com/joaomdmoura/crewAI-tools)
- [ChromaDB Documentation](https://docs.trychroma.com)

---

**Last Updated**: 2025-12-11
**Component Count**: 97 tools (90 official + 7 studio)
**RAG Engine**: ChromaDB with semantic search
**Version**: 0.1.0
