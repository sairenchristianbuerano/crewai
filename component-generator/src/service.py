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


@app.get("/api/crewai/component-generator/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crewai-component-generator",
        "version": "0.1.0",
        "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    }


@app.post("/api/crewai/component-generator/generate")
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
        "documentation": "<Tool usage documentation>"
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

        # Return response in Flowise-compatible format
        return {
            "code": result.tool_code,
            "documentation": result.documentation or ""
        }

    except yaml.YAMLError as e:
        logger.error("YAML parsing failed", error=str(e))
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")
    except Exception as e:
        logger.error("Tool generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/crewai/component-generator/generate/sample")
async def generate_sample_tool_endpoint():
    """
    Generate a sample crewAI tool using built-in specification

    No request body required. Uses a pre-defined sample specification
    to demonstrate the tool generation capabilities.

    Response:
    {
        "code": "<Generated Python code>",
        "documentation": "<Tool usage documentation>"
    }
    """
    if not generator:
        raise HTTPException(status_code=503, detail="Generator not initialized")

    try:
        # Load sample specification from file
        sample_spec_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "sample_spec.yaml"
        )

        with open(sample_spec_path, "r") as f:
            sample_spec_yaml = f.read()

        logger.info("Generating sample tool from built-in specification")
        spec_dict = yaml.safe_load(sample_spec_yaml)

        # Convert to ToolSpec
        spec = ToolSpec(**spec_dict)

        logger.info("Generating sample crewAI tool", tool_name=spec.name)
        result = await generator.generate_tool(spec)

        logger.info(
            "Sample tool generated successfully",
            tool_name=spec.name,
            code_size=len(result.tool_code),
            is_valid=result.validation.is_valid
        )

        # Return response in Flowise-compatible format
        return {
            "code": result.tool_code,
            "documentation": result.documentation or ""
        }

    except FileNotFoundError:
        logger.error("Sample specification file not found")
        raise HTTPException(status_code=500, detail="Sample specification file not found")
    except yaml.YAMLError as e:
        logger.error("Sample YAML parsing failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Invalid sample YAML: {str(e)}")
    except Exception as e:
        logger.error("Sample tool generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/crewai/component-generator/assess")
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
