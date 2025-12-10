# Folder Structure & Naming Update

**Date:** 2025-12-10
**Status:** ✅ Updated

---

## 📁 Folder Naming Changes

### Previous Names ❌
- `crewai-tool-generator`
- `crewai-tool-index`

### **New Names** ✅
- `component-generator`
- `component-index`

---

## 🗂️ Complete Project Structure

```
crewai/
├── README.md
├── ROADMAP.md
├── IMPLEMENTATION_SUMMARY.md
├── FOLDER_STRUCTURE_UPDATE.md          ← This file
├── docker-compose.yml                   ✅ Updated
├── .env.example                         ✅ Updated
├── LICENSE
│
├── component-generator/                 ✅ Renamed from crewai-tool-generator
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── sample_spec.yaml
│   ├── src/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── crewai_agent.py
│   │   ├── crewai_validator.py
│   │   └── base_classes.py
│   ├── templates/                       (Optional - not required)
│   ├── data/                            (Runtime data)
│   └── tests/
│
├── component-index/                     ✅ Renamed from crewai-tool-index
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── service.py                   ✅ Updated paths
│   │   ├── models.py
│   │   ├── storage.py
│   │   └── crewai_rag_engine.py        ✅ Updated paths
│   ├── data/
│   │   ├── components/                  📊 Component registry (JSON)
│   │   │   └── index.json              (Generated at runtime)
│   │   │
│   │   ├── crewai_components/          ✅ NEW: CrewAI-Studio components
│   │   │   └── tools/                  ✅ Copied from CrewAI-Studio
│   │   │       ├── CustomApiTool.py
│   │   │       ├── DuckDuckGoSearchTool.py
│   │   │       ├── CustomFileWriteTool.py
│   │   │       └── ...
│   │   │
│   │   └── chromadb/                   🗄️ ChromaDB vector database
│   │       ├── chroma.sqlite3          (Generated at runtime)
│   │       └── {uuid}/                 (Generated at runtime)
│   │           └── (embedding files)
│   └── tests/
│
└── docs/
    └── examples/
        ├── search_tool_spec.yaml
        └── file_tool_spec.yaml
```

---

## 🎯 Key Directory Purposes

### **component-generator/** (Port 8085)
**Purpose:** Generates crewAI tool code using Claude AI

**Data Directory:**
- `data/` - Runtime data (mostly empty, no ChromaDB here)

---

### **component-index/** (Port 8086)
**Purpose:** Indexes and catalogs tools with semantic search

**Data Directories:**

1. **`data/components/`** - Component Registry
   - `index.json` - JSON database of all registered tools
   - Stores metadata for generated components
   - Created/updated at runtime

2. **`data/crewai_components/`** - **NEW!** Knowledge Base
   - `tools/` - **Copied from CrewAI-Studio**
   - Contains reference tool implementations
   - Used by RAG engine for pattern matching
   - **Source:** `C:\Users\Joana\Desktop\sairen-files\github\env\CrewAI-Studio\app\tools`

3. **`data/chromadb/`** - **ChromaDB Vector Database**
   - `chroma.sqlite3` - SQLite database for ChromaDB
   - `{uuid}/` - UUID-named folders with embedding files
   - Stores vector embeddings of tools
   - **Created automatically at runtime**
   - **NOT in component-generator** (only in component-index)

---

## ⚙️ Environment Variables Updated

### `.env.example` Changes

```bash
# OLD (❌):
CREWAI_STUDIO_TOOLS_PATH=

# NEW (✅):
CREWAI_STUDIO_TOOLS_PATH=C:\Users\Joana\Desktop\sairen-files\github\env\CrewAI-Studio\app
```

---

## 🐳 Docker Compose Changes

### Service Names

```yaml
# OLD (❌):
services:
  tool-generator:
    build:
      context: ./crewai-tool-generator
    container_name: crewai-tool-generator

  tool-index:
    build:
      context: ./crewai-tool-index
    container_name: crewai-tool-index

# NEW (✅):
services:
  component-generator:
    build:
      context: ./component-generator
    container_name: crewai-component-generator

  component-index:
    build:
      context: ./component-index
    container_name: crewai-component-index
```

### Volume Mounts

```yaml
# component-index service:
volumes:
  - index_data:/app/data
  # NEW: Mount crewai_components folder
  - ${CREWAI_STUDIO_TOOLS_PATH:-./component-index/data/crewai_components}:/app/data/crewai_components:ro
```

### Environment Variables

```yaml
# component-index service:
environment:
  - STORAGE_PATH=/app/data/components
  - TOOLS_DIR=/app/data/crewai_components/tools  # ✅ Updated
  - CHROMADB_DIR=/app/data/chromadb
```

---

## 📊 ChromaDB Location - CLARIFIED

### ⚠️ IMPORTANT: ChromaDB is ONLY in component-index

**Correct Location:**
```
component-index/data/chromadb/
├── chroma.sqlite3              # SQLite database
└── {uuid-folder}/              # Embedding files
    ├── data_level0.bin
    ├── header.bin
    ├── index_metadata.pickle
    └── length.bin
```

**NOT in component-generator** (generator doesn't use ChromaDB)

### How ChromaDB is Created

1. **First startup** of component-index service
2. RAG engine initializes ChromaDB
3. Scans `/app/data/crewai_components/tools/` for Python files
4. Creates embeddings and stores in ChromaDB
5. UUID folders created automatically by ChromaDB

---

## 🔄 Updated File References

### Code Files Updated

| File | Change | Status |
|------|--------|--------|
| `docker-compose.yml` | Folder names, paths | ✅ Updated |
| `component-index/src/service.py` | TOOLS_DIR path | ✅ Updated |
| `component-index/src/crewai_rag_engine.py` | Default path | ✅ Updated |

### Documentation Files to Update

| File | Needs Update | Priority |
|------|--------------|----------|
| `README.md` | Folder references | 🔴 High |
| `ROADMAP.md` | Folder references | 🟡 Medium |
| `IMPLEMENTATION_SUMMARY.md` | Folder references | 🟡 Medium |
| `component-generator/README.md` | Service name | 🟡 Medium |
| `component-index/README.md` | Service name, paths | 🟡 Medium |

---

## 🚀 Quick Start (Updated)

```bash
# 1. Navigate to project
cd C:\Users\Joana\Desktop\sairen-files\github\repo\crewai

# 2. Set environment
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY

# 3. Start services (NEW service names)
docker-compose up -d

# 4. Check health
curl http://localhost:8085/api/crewai/tool-generator/health
curl http://localhost:8086/api/crewai/tool-index/health

# 5. View logs (NEW container names)
docker logs crewai-component-generator -f
docker logs crewai-component-index -f
```

---

## 📝 Verification Checklist

### Files in Place

- [x] CrewAI-Studio tools copied to `component-index/data/crewai_components/tools/`
- [x] 7 tools copied successfully
- [x] Docker Compose updated with new names
- [x] Service code updated with new paths
- [x] ChromaDB will be created in `component-index/data/chromadb/` at runtime

### Environment Setup

- [ ] `.env` file created (from `.env.example`)
- [ ] `ANTHROPIC_API_KEY` set in `.env`
- [ ] Optional: `CREWAI_STUDIO_TOOLS_PATH` set if using external mount

### Docker Services

- [ ] Services build successfully
- [ ] component-generator starts on port 8085
- [ ] component-index starts on port 8086
- [ ] Health checks pass
- [ ] ChromaDB initializes and indexes tools

---

## 🐛 Common Issues & Solutions

### Issue: ChromaDB folder empty

**Solution:**
- ChromaDB creates files at **runtime**, not build time
- Start the component-index service
- Check logs: `docker logs crewai-component-index -f`
- Look for "ChromaDB initialized" message
- UUID folders appear after first indexing

### Issue: No tools found

**Solution:**
- Check `component-index/data/crewai_components/tools/` has Python files
- Verify TOOLS_DIR environment variable
- Check docker-compose volume mount
- Restart component-index service

### Issue: Services won't start

**Solution:**
- Check folder names match docker-compose.yml
- Verify paths in docker-compose.yml
- Run `docker-compose down` then `docker-compose up -d`

---

## 📚 Updated Documentation Structure

All documentation now uses:
- ✅ `component-generator` (not crewai-tool-generator)
- ✅ `component-index` (not crewai-tool-index)
- ✅ `crewai_components` folder for knowledge base
- ✅ ChromaDB only in component-index
- ✅ Correct paths for all directories

---

**Summary:** All folder names updated, paths corrected, CrewAI-Studio components copied, and ChromaDB location clarified (component-index only).

**Next:** Update main documentation files with new folder names.
