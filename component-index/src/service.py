"""
FastAPI service for CrewAI Tool Index

REST API service for tool registry and tracking.
Endpoint prefix: /api/crewai/*
"""

import os
import uuid
from typing import Optional, List
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import ToolMetadata, ToolRegistrationRequest, ToolListResponse
from storage import ToolStorage
from crewai_rag_engine import CrewAIRAGEngine

logger = structlog.get_logger()

# Storage instance
storage: Optional[ToolStorage] = None

# RAG Pattern Engine
pattern_engine: Optional[CrewAIRAGEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    global storage, pattern_engine

    logger.info("Starting CrewAI Tool Index service")

    # Initialize storage
    storage_path = os.getenv("STORAGE_PATH", "/app/data/components")
    storage = ToolStorage(storage_path=storage_path)

    logger.info("Tool storage initialized", path=storage_path)

    # Initialize RAG pattern engine
    tools_directory = os.getenv("TOOLS_DIR", "/app/data/crewai_components/tools")
    chromadb_dir = os.getenv("CHROMADB_DIR", "/app/data/chromadb")

    try:
        pattern_engine = CrewAIRAGEngine(
            tools_directory=tools_directory,
            persist_directory=chromadb_dir
        )

        pattern_count = pattern_engine.index_tools()
        logger.info("Pattern engine initialized", patterns_indexed=pattern_count)
    except Exception as e:
        logger.warning("Pattern engine initialization failed", error=str(e))
        logger.warning("Pattern search endpoints will not be available")

    yield

    # Shutdown
    logger.info("Shutting down CrewAI Tool Index")


# FastAPI app
app = FastAPI(
    title="CrewAI Tool Index",
    version="0.1.0",
    description="Tool registry and tracking for crewAI tools",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost:8085", "http://localhost:3000"]')
# Parse JSON string to list
import json
allowed_origins = json.loads(cors_origins) if isinstance(cors_origins, str) else cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/api/crewai/tool-index/health")
async def health_check():
    """Health check endpoint"""
    stats = storage.get_stats() if storage else {}

    # Include pattern engine status
    pattern_stats = None
    if pattern_engine:
        try:
            pattern_stats = pattern_engine.get_stats()
        except Exception as e:
            logger.warning("Failed to get pattern stats", error=str(e))

    return {
        "status": "healthy",
        "service": "crewai-tool-index",
        "version": "0.1.0",
        "stats": stats,
        "pattern_engine": pattern_stats
    }


@app.post("/api/crewai/tools/register", response_model=ToolMetadata)
async def register_tool(request: ToolRegistrationRequest):
    """
    Register a generated tool in the index

    This endpoint stores metadata about generated tools for tracking purposes.
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        # Create metadata with generated ID
        metadata = ToolMetadata(
            tool_id=str(uuid.uuid4()),
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            category=request.category,
            platform=request.platform,
            version=request.version,
            author=request.author,
            code_size=request.code_size,
            dependencies=request.dependencies,
            validation_passed=request.validation_passed,
            deployment_status=request.deployment_status,
            input_schema=request.input_schema,
            has_config_params=request.has_config_params,
            requirements=request.requirements
        )

        # Register in storage
        registered = storage.register_tool(metadata)

        logger.info("Tool registered", tool_id=registered.tool_id, name=registered.name)

        return registered
    except Exception as e:
        logger.error("Tool registration failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crewai/tools", response_model=ToolListResponse)
async def list_tools(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List all registered tools with optional filters

    Query parameters:
    - platform: Filter by platform (e.g., 'crewai')
    - category: Filter by category (e.g., 'api', 'search', 'file')
    - limit: Maximum number of results (default: 100)
    - offset: Pagination offset (default: 0)
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        tools = storage.list_tools(
            platform=platform,
            category=category,
            limit=limit,
            offset=offset
        )

        # Get total count (without pagination)
        all_tools = storage.list_tools(platform=platform, category=category, limit=10000)
        total = len(all_tools)

        return ToolListResponse(
            total=total,
            tools=tools
        )
    except Exception as e:
        logger.error("Tool listing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crewai/tools/stats")
async def get_stats():
    """
    Get tool index statistics
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        stats = storage.get_stats()
        return stats
    except Exception as e:
        logger.error("Stats retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crewai/tools/name/{name}", response_model=ToolMetadata)
async def get_tool_by_name(name: str):
    """
    Get tool metadata by name (returns latest version)
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        tool = storage.get_tool_by_name(name)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool not found: {name}")

        return tool
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Tool retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crewai/tools/{tool_id}", response_model=ToolMetadata)
async def get_tool(tool_id: str):
    """
    Get tool metadata by ID
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        tool = storage.get_tool(tool_id)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}")

        return tool
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Tool retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/crewai/tools/{tool_id}/deployment")
async def update_deployment_status(
    tool_id: str,
    status: str = Query(..., description="Deployment status")
):
    """
    Update deployment status of a tool
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        success = storage.update_deployment_status(tool_id, status)

        if not success:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}")

        return {"tool_id": tool_id, "deployment_status": status, "updated": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Deployment status update failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/crewai/tools/{tool_id}")
async def delete_tool(tool_id: str):
    """
    Delete a tool from the index
    """
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")

    try:
        success = storage.delete_tool(tool_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}")

        return {"tool_id": tool_id, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Tool deletion failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PATTERN SEARCH ENDPOINTS (RAG)
# ============================================================================

class PatternSearchRequest(BaseModel):
    """Request for pattern search"""
    query: str
    n_results: int = 5
    category: Optional[str] = None


class PatternSimilarRequest(BaseModel):
    """Request for finding similar patterns"""
    description: str
    category: Optional[str] = None
    input_types: Optional[List[str]] = None
    n_results: int = 3


class PatternIndexRequest(BaseModel):
    """Request for reindexing patterns"""
    force_reindex: bool = False


@app.post("/api/crewai/patterns/search")
async def search_patterns(request: PatternSearchRequest):
    """
    Search tool patterns using semantic search

    This endpoint searches the knowledge base of reference tool patterns
    to help guide code generation with similar examples.
    """
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not initialized")

    try:
        # Build filters if category specified
        filters = {'category': request.category} if request.category else None

        results = pattern_engine.search(
            query=request.query,
            n_results=request.n_results,
            filters=filters
        )

        return {
            "query": request.query,
            "results_count": len(results),
            "results": results,
            "platform": "crewai"
        }
    except Exception as e:
        logger.error("Pattern search failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/crewai/patterns/similar")
async def find_similar_patterns(request: PatternSimilarRequest):
    """
    Find tool patterns similar to a description

    Used by the tool generator to find reference implementations
    that match the specification being generated.
    """
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not initialized")

    try:
        results = pattern_engine.find_similar_tools(
            description=request.description,
            category=request.category,
            input_types=request.input_types,
            n_results=request.n_results
        )

        return {
            "description": request.description,
            "results_count": len(results),
            "results": results,
            "platform": "crewai"
        }
    except Exception as e:
        logger.error("Similar pattern search failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/crewai/patterns/index")
async def reindex_patterns(request: PatternIndexRequest):
    """
    Reindex tool patterns from the knowledge base
    """
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not initialized")

    try:
        count = pattern_engine.index_tools(force_reindex=request.force_reindex)

        return {
            "status": "success",
            "tools_indexed": count,
            "force_reindex": request.force_reindex,
            "platform": "crewai"
        }
    except Exception as e:
        logger.error("Pattern reindexing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crewai/patterns/stats")
async def get_pattern_stats():
    """
    Get pattern knowledge base statistics
    """
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not initialized")

    try:
        stats = pattern_engine.get_stats()
        return stats
    except Exception as e:
        logger.error("Pattern stats retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crewai/patterns/{pattern_name}")
async def get_pattern_by_name(pattern_name: str):
    """
    Get a specific tool pattern by name
    """
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not initialized")

    try:
        pattern = pattern_engine.get_tool_by_name(pattern_name)

        if not pattern:
            raise HTTPException(status_code=404, detail=f"Pattern not found: {pattern_name}")

        return pattern
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Pattern retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8086"))

    uvicorn.run(
        "service:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    )
