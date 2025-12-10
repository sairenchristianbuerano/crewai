# CrewAI Component Generation Services - API Reference

> Complete API documentation for Component Generator and Component Index services

**Version:** 1.0.0
**Base URLs:**
- Component Generator: `http://localhost:8085`
- Component Index: `http://localhost:8086`

---

## Table of Contents

- [Component Generator API](#component-generator-api)
  - [Health Check](#generator-health-check)
  - [Generate Tool](#generate-tool)
  - [Generate Sample Tool](#generate-sample-tool)
  - [Assess Feasibility](#assess-feasibility)
- [Component Index API](#component-index-api)
  - [Health Check](#index-health-check)
  - [Tool Registry Endpoints](#tool-registry-endpoints)
  - [Pattern Search Endpoints](#pattern-search-endpoints-rag)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Examples](#examples)

---

## Component Generator API

**Service:** Component Generator
**Port:** 8085
**Base URL:** `http://localhost:8085`

### Generator Health Check

Check the health and status of the Component Generator service.

```http
GET /api/crewai/tool-generator/health
```

**Response 200:**
```json
{
  "status": "healthy",
  "service": "crewai-component-generator",
  "version": "0.1.0",
  "model": "claude-sonnet-4-20250514"
}
```

---

### Generate Tool

Generate a crewAI BaseTool component from a YAML specification.

```http
POST /api/crewai/tool-generator/generate
Content-Type: application/json
```

**Request Body:**
```json
{
  "spec": "name: CustomApiTool\ndisplay_name: \"API Caller\"\ndescription: \"Make HTTP API calls\"\ncategory: api\nplatforms:\n  - crewai\nrequirements:\n  - \"Support GET, POST methods\"\ninputs:\n  - name: endpoint\n    type: str\n    required: true\nauthor: \"Your Name\"\nversion: \"1.0.0\""
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spec` | string | Yes | YAML specification as string |

**YAML Specification Format:**

```yaml
name: ToolName                # PascalCase class name
display_name: "Display Name"  # Human-readable name
description: "Tool description"
category: api                 # api, search, file, database, custom
platforms:
  - crewai

requirements:                 # List of functional requirements
  - "Requirement 1"
  - "Requirement 2"

inputs:                       # Tool input parameters
  - name: param1
    type: str
    description: "Parameter description"
    required: true

config_params:                # Optional __init__ parameters
  - name: config1
    type: "Optional[str]"
    description: "Config parameter"

dependencies:                 # Python package dependencies
  - "requests"

author: "Your Name"
version: "1.0.0"
```

**Response 200:**
```json
{
  "code": "from typing import Optional, Dict, Any, Type\nfrom crewai.tools import BaseTool\n...",
  "documentation": "# CustomApiTool\n\nVersion: 1.0.0\n...",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "suggestions": []
  },
  "dependencies": ["requests"],
  "deployment_instructions": {
    "usage": "from generated_tools.customapitool import CustomApiTool",
    "dependencies": ["requests"],
    "install_command": "pip install requests"
  },
  "tool_config": {
    "name": "CustomApiTool",
    "display_name": "API Caller",
    "category": "api",
    "version": "1.0.0",
    "author": "Your Name"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Generated Python code for the tool |
| `documentation` | string | Markdown documentation for usage |
| `validation` | object | Validation results |
| `validation.is_valid` | boolean | Whether code passed validation |
| `validation.errors` | array | List of validation errors |
| `validation.warnings` | array | List of warnings |
| `validation.suggestions` | array | Improvement suggestions |
| `dependencies` | array | Required Python packages |
| `deployment_instructions` | object | How to deploy the tool |
| `tool_config` | object | Tool metadata |

**Error Responses:**

**400 Bad Request:**
```json
{
  "detail": "Invalid YAML: ..."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error message"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Generator not initialized"
}
```

---

### Generate Sample Tool

Generate a sample crewAI tool using a built-in specification file.

```http
POST /api/crewai/tool-generator/generate/sample
Content-Type: application/json
```

**Request Body:** None required

**Description:**
This endpoint demonstrates the tool generation capabilities by generating a sample tool from a pre-defined specification. No request body is needed - the endpoint uses a built-in sample specification file.

**Example Request:**
```bash
curl -X POST http://localhost:8085/api/crewai/tool-generator/generate/sample \
  -H "Content-Type: application/json"
```

**Response 200:**
```json
{
  "code": "from typing import Optional, Dict, Any, Type\nfrom crewai.tools import BaseTool\n...",
  "documentation": "# PlaygroundCalculator\n\nVersion: 1.0.0\n...",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "suggestions": []
  },
  "dependencies": ["math", "numpy"],
  "deployment_instructions": {
    "usage": "from generated_tools.playgroundcalculator import PlaygroundCalculator",
    "dependencies": ["math", "numpy"],
    "install_command": "pip install numpy"
  },
  "tool_config": {
    "name": "PlaygroundCalculator",
    "display_name": "Playground Calculator",
    "category": "tools",
    "version": "1.0.0",
    "author": "CrewAI Component Factory"
  }
}
```

**Response Fields:** Same as `/generate` endpoint

**Error Responses:**

**500 Internal Server Error:**
```json
{
  "detail": "Sample specification file not found"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Generator not initialized"
}
```

**Use Cases:**
- Testing the API without creating a specification
- Seeing a reference example of generated code
- Validating the service is working correctly
- Understanding the response format

---

### Assess Feasibility

Assess the feasibility of generating a tool before attempting full generation.

```http
POST /api/crewai/tool-generator/assess
Content-Type: application/json
```

**Request Body:**
```json
{
  "spec": "name: WebScraperTool\ndescription: \"Scrape websites\"\ncategory: web\nplatforms:\n  - crewai"
}
```

**Response 200:**
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

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `feasible` | boolean | Whether generation is feasible |
| `confidence` | string | Confidence level: `high`, `medium`, `low`, `blocked` |
| `complexity` | string | Complexity: `simple`, `medium`, `complex` |
| `issues` | array | Issues found in specification |
| `suggestions` | array | Suggestions for improvement |
| `missing_info` | array | Required information that's missing |
| `similar_patterns_found` | number | Number of similar patterns found in RAG |

---

## Component Index API

**Service:** Component Index
**Port:** 8086
**Base URL:** `http://localhost:8086`

### Index Health Check

Check the health and status of the Component Index service.

```http
GET /api/crewai/tool-index/health
```

**Response 200:**
```json
{
  "status": "healthy",
  "service": "crewai-component-index",
  "version": "0.1.0",
  "stats": {
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
  },
  "pattern_engine": {
    "total_tools": 7,
    "has_embeddings": true
  }
}
```

---

## Tool Registry Endpoints

### Register Tool

Register a newly generated tool in the index.

```http
POST /api/crewai/tools/register
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "CustomApiTool",
  "display_name": "API Caller",
  "description": "Make HTTP API calls with custom parameters",
  "category": "api",
  "platform": "crewai",
  "version": "1.0.0",
  "author": "Component Factory",
  "code_size": 2048,
  "dependencies": ["requests"],
  "validation_passed": true,
  "deployment_status": null,
  "input_schema": {
    "endpoint": {"type": "str", "required": true},
    "method": {"type": "str", "required": true}
  },
  "has_config_params": true,
  "requirements": [
    "Support GET, POST, PUT, DELETE methods",
    "Accept custom headers"
  ]
}
```

**Response 200:**
```json
{
  "tool_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "CustomApiTool",
  "display_name": "API Caller",
  "description": "Make HTTP API calls with custom parameters",
  "category": "api",
  "platform": "crewai",
  "version": "1.0.0",
  "created_at": "2025-12-10T10:00:00.000Z",
  "updated_at": "2025-12-10T10:00:00.000Z",
  "author": "Component Factory",
  "status": "generated",
  "code_size": 2048,
  "dependencies": ["requests"],
  "validation_passed": true,
  "deployment_status": null,
  "input_schema": {...},
  "has_config_params": true,
  "requirements": [...]
}
```

---

### List Tools

Retrieve a list of all registered tools with optional filtering and pagination.

```http
GET /api/crewai/tools?platform=crewai&category=api&limit=10&offset=0
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `platform` | string | No | - | Filter by platform (e.g., `crewai`) |
| `category` | string | No | - | Filter by category (e.g., `api`, `search`) |
| `limit` | integer | No | 100 | Maximum results (1-1000) |
| `offset` | integer | No | 0 | Pagination offset |

**Response 200:**
```json
{
  "total": 15,
  "tools": [
    {
      "tool_id": "550e8400-...",
      "name": "CustomApiTool",
      "display_name": "API Caller",
      "description": "Make HTTP API calls",
      "category": "api",
      "platform": "crewai",
      "version": "1.0.0",
      "created_at": "2025-12-10T10:00:00.000Z",
      "updated_at": "2025-12-10T10:00:00.000Z",
      "author": "User",
      "status": "generated",
      "code_size": 2048,
      "dependencies": ["requests"],
      "validation_passed": true,
      "deployment_status": null
    }
  ]
}
```

---

### Get Tool by ID

Retrieve a specific tool by its unique ID.

```http
GET /api/crewai/tools/{tool_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tool_id` | string (UUID) | Yes | Unique tool identifier |

**Response 200:**
```json
{
  "tool_id": "550e8400-...",
  "name": "CustomApiTool",
  ...
}
```

**Error 404:**
```json
{
  "detail": "Tool not found: 550e8400-..."
}
```

---

### Get Tool by Name

Retrieve the latest version of a tool by its name.

```http
GET /api/crewai/tools/name/{name}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Tool class name (e.g., `CustomApiTool`) |

**Response 200:**
```json
{
  "tool_id": "550e8400-...",
  "name": "CustomApiTool",
  "version": "1.0.0",
  ...
}
```

---

### Update Deployment Status

Update the deployment status of a tool.

```http
PATCH /api/crewai/tools/{tool_id}/deployment?status=deployed
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | Yes | New deployment status |

**Response 200:**
```json
{
  "tool_id": "550e8400-...",
  "deployment_status": "deployed",
  "updated": true
}
```

---

### Delete Tool

Remove a tool from the index.

```http
DELETE /api/crewai/tools/{tool_id}
```

**Response 200:**
```json
{
  "tool_id": "550e8400-...",
  "deleted": true
}
```

---

### Get Statistics

Retrieve comprehensive statistics about indexed tools.

```http
GET /api/crewai/tools/stats
```

**Response 200:**
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

---

## Pattern Search Endpoints (RAG)

### Search Patterns

Perform semantic search over tool patterns using natural language queries.

```http
POST /api/crewai/patterns/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "tool that makes HTTP requests",
  "n_results": 5,
  "category": "api"
}
```

**Request Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | Natural language search query |
| `n_results` | integer | No | 5 | Number of results to return |
| `category` | string | No | - | Filter by category |

**Response 200:**
```json
{
  "query": "tool that makes HTTP requests",
  "results_count": 5,
  "results": [
    {
      "name": "CustomApiTool",
      "code": "from crewai.tools import BaseTool...",
      "metadata": {
        "name": "CustomApiTool",
        "description": "Make HTTP API calls",
        "category": "api"
      },
      "similarity": 0.89
    }
  ],
  "platform": "crewai"
}
```

---

### Find Similar Patterns

Find tool patterns similar to a given description.

```http
POST /api/crewai/patterns/similar
Content-Type: application/json
```

**Request Body:**
```json
{
  "description": "A tool that searches the web using DuckDuckGo",
  "category": "search",
  "input_types": ["query", "max_results"],
  "n_results": 3
}
```

**Request Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `description` | string | Yes | - | Tool description to match |
| `category` | string | No | - | Filter by category |
| `input_types` | array | No | - | Expected input parameter types |
| `n_results` | integer | No | 3 | Number of results |

**Response 200:**
```json
{
  "description": "A tool that searches the web using DuckDuckGo",
  "results_count": 3,
  "results": [
    {
      "name": "DuckDuckGoSearchTool",
      "category": "search",
      "code": "...",
      "inputs": ["query", "max_results"],
      "outputs": ["str"]
    }
  ],
  "platform": "crewai"
}
```

---

### Get Pattern by Name

Retrieve a specific pattern by name from the knowledge base.

```http
GET /api/crewai/patterns/{pattern_name}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern_name` | string | Yes | Pattern/tool name |

**Response 200:**
```json
{
  "name": "CustomApiTool",
  "code": "from crewai.tools import BaseTool...",
  "metadata": {
    "name": "CustomApiTool",
    "description": "...",
    "category": "api"
  }
}
```

---

### Reindex Patterns

Trigger reindexing of tool patterns from the knowledge base.

```http
POST /api/crewai/patterns/index
Content-Type: application/json
```

**Request Body:**
```json
{
  "force_reindex": false
}
```

**Response 200:**
```json
{
  "status": "success",
  "tools_indexed": 7,
  "force_reindex": false,
  "platform": "crewai"
}
```

---

### Get Pattern Statistics

Retrieve statistics about the pattern knowledge base.

```http
GET /api/crewai/patterns/stats
```

**Response 200:**
```json
{
  "total_tools": 7,
  "has_embeddings": true
}
```

---

## Authentication

Currently, both services do not require authentication. API keys are used internally for Claude AI integration but are not exposed in the API.

**Note:** In production environments, you should implement:
- API key authentication
- Rate limiting
- Request signing
- CORS configuration

---

## Error Handling

All endpoints use standard HTTP status codes and return errors in a consistent format:

**Error Response Format:**
```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters or body |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service not initialized |

---

## Rate Limits

Currently, no rate limits are enforced. For production use, consider implementing:

- **Per-IP rate limiting:** 100 requests/minute
- **Per-endpoint limits:** Generation endpoints may have lower limits due to AI processing time

---

## Examples

### Complete Workflow: Generate and Register a Tool

**Step 1: Assess Feasibility**
```bash
curl -X POST http://localhost:8085/api/crewai/tool-generator/assess \
  -H "Content-Type: application/json" \
  -d '{"spec": "name: MyTool\ndescription: Test tool\ncategory: custom"}'
```

**Step 2: Generate Tool**
```bash
curl -X POST http://localhost:8085/api/crewai/tool-generator/generate \
  -H "Content-Type: application/json" \
  -d "{\"spec\": \"$(cat my_tool_spec.yaml)\"}" > generated_tool.json
```

**Step 3: Register in Index**
```bash
curl -X POST http://localhost:8086/api/crewai/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyTool",
    "display_name": "My Custom Tool",
    "description": "A custom tool for testing",
    "category": "custom",
    "platform": "crewai",
    "author": "Developer",
    "code_size": 1024,
    "validation_passed": true
  }'
```

**Step 4: Search for Similar Tools**
```bash
curl -X POST http://localhost:8086/api/crewai/patterns/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "custom tool for testing",
    "n_results": 5
  }'
```

**Step 5: List All Tools**
```bash
curl "http://localhost:8086/api/crewai/tools?category=custom&limit=10"
```

---

### Search and Filter Examples

**Filter by Category:**
```bash
curl "http://localhost:8086/api/crewai/tools?category=api"
```

**Pagination:**
```bash
# First page
curl "http://localhost:8086/api/crewai/tools?limit=10&offset=0"

# Second page
curl "http://localhost:8086/api/crewai/tools?limit=10&offset=10"
```

**Combined Filters:**
```bash
curl "http://localhost:8086/api/crewai/tools?platform=crewai&category=search&limit=5"
```

---

### Pattern Search Examples

**Natural Language Search:**
```bash
curl -X POST http://localhost:8086/api/crewai/patterns/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "tool that scrapes websites",
    "n_results": 3
  }'
```

**Category-Specific Search:**
```bash
curl -X POST http://localhost:8086/api/crewai/patterns/similar \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Search the web for information",
    "category": "search",
    "n_results": 5
  }'
```

---

## Interactive API Documentation

Both services provide interactive Swagger UI documentation:

- **Component Generator:** http://localhost:8085/docs
- **Component Index:** http://localhost:8086/docs

### ReDoc Documentation

Alternative ReDoc interface:

- **Component Generator:** http://localhost:8085/redoc
- **Component Index:** http://localhost:8086/redoc

---

## API Versioning

Current API version: **v1** (implied in all endpoints)

Future versions will use explicit versioning:
- `/api/v2/crewai/...`

---

## Support

- **GitHub Repository:** https://github.com/sairenchristianbuerano/crewai
- **Documentation:** See [README.md](README.md) and service-specific READMEs
- **Health Checks:** Monitor service health via `/health` endpoints

---

**Last Updated:** 2025-12-10
**API Version:** 1.0.0
**Services:** Component Generator v0.1.0, Component Index v0.1.0
