"""
FastAPI service for CrewAI Tool Generator

REST API service for crewAI custom tool generation.
Endpoint prefix: /api/crewai/*
"""

import os
import yaml
from typing import Optional
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crewai_agent import CrewAIToolGenerator
from crewai_validator import CrewAIFeasibilityChecker
from base_classes import ToolSpec, GeneratedTool

logger = structlog.get_logger()

# Generator instances
generator: Optional[CrewAIToolGenerator] = None
feasibility_checker: Optional[CrewAIFeasibilityChecker] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    global generator, feasibility_checker

    logger.info("Starting CrewAI Tool Generator service")

    # Initialize generator
    rag_service_url = os.getenv("RAG_SERVICE_URL", "http://localhost:8086")

    generator = CrewAIToolGenerator(rag_service_url=rag_service_url)
    feasibility_checker = CrewAIFeasibilityChecker()

    logger.info("CrewAI Tool Generator and Feasibility Checker initialized")

    yield

    # Shutdown
    logger.info("Shutting down CrewAI Tool Generator")


# FastAPI app
app = FastAPI(
    title="CrewAI Tool Generator",
    version="0.1.0",
    description="Generate custom crewAI tool components from YAML specifications",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost:8086", "http://localhost:3000"]')
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


class GenerateRequest(BaseModel):
    """Request model for tool generation"""
    spec: str


@app.get("/api/crewai/tool-generator/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crewai-tool-generator",
        "version": "0.1.0",
        "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    }


@app.post("/api/crewai/tool-generator/generate")
async def generate_tool_endpoint(request: GenerateRequest):
    """
    Generate custom crewAI tool from YAML specification

    Request body:
    {
        "spec": "<YAML specification string>"
    }

    Response:
    {
        "code": "<Generated Python code>",
        "documentation": "<Tool usage documentation>",
        "validation": {
            "is_valid": true,
            "errors": [],
            "warnings": []
        },
        "dependencies": ["requests"],
        "deployment_instructions": {...}
    }
    """
    if not generator:
        raise HTTPException(status_code=503, detail="Generator not initialized")

    try:
        # Parse YAML specification
        logger.info("Parsing tool specification from YAML")
        spec_dict = yaml.safe_load(request.spec)

        # Convert to ToolSpec
        spec = ToolSpec(**spec_dict)

        logger.info("Generating crewAI tool", tool_name=spec.name)
        result = await generator.generate_tool(spec)

        logger.info(
            "Tool generated successfully",
            tool_name=spec.name,
            code_size=len(result.tool_code),
            is_valid=result.validation.is_valid
        )

        # Return complete response
        return {
            "code": result.tool_code,
            "documentation": result.documentation or "",
            "validation": {
                "is_valid": result.validation.is_valid,
                "errors": result.validation.errors,
                "warnings": result.validation.warnings,
                "suggestions": result.validation.suggestions
            },
            "dependencies": result.dependencies,
            "deployment_instructions": result.deployment_instructions,
            "tool_config": result.tool_config
        }

    except yaml.YAMLError as e:
        logger.error("YAML parsing failed", error=str(e))
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")
    except Exception as e:
        logger.error("Tool generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/crewai/tool-generator/assess")
async def assess_feasibility_endpoint(request: GenerateRequest):
    """
    Assess feasibility of generating a crewAI tool before attempting generation

    Request body:
    {
        "spec": "<YAML specification string>"
    }

    Returns feasibility analysis including:
    - Whether generation is feasible
    - Confidence level (high/medium/low/blocked)
    - Issues found
    - Suggestions for improvement
    - Missing information needed
    """
    if not feasibility_checker or not generator:
        raise HTTPException(status_code=503, detail="Services not initialized")

    try:
        # Parse YAML specification
        logger.info("Parsing tool specification from YAML for assessment")
        spec_dict = yaml.safe_load(request.spec)

        # Convert to ToolSpec
        spec = ToolSpec(**spec_dict)

        # Get RAG context for pattern matching
        rag_context = await generator._retrieve_similar_components(spec)

        # Run feasibility assessment
        assessment = await feasibility_checker.assess(
            spec.model_dump(),
            rag_context=rag_context
        )

        return assessment.to_dict()

    except yaml.YAMLError as e:
        logger.error("YAML parsing failed", error=str(e))
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")
    except Exception as e:
        logger.error("Feasibility assessment failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8085"))

    uvicorn.run(
        "service:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    )
