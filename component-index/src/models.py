"""
Data models for CrewAI Tool Index
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata for a generated crewAI tool"""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Tool class name (PascalCase, e.g., 'CustomApiTool')")
    display_name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="Tool description")
    category: str = Field(..., description="Tool category (api, search, file, database, custom)")
    platform: str = Field(default="crewai", description="Target platform")
    version: str = Field(default="1.0.0", description="Tool version")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    author: str = Field(..., description="Tool author")
    status: str = Field(default="generated", description="Tool status (generated, deployed, deprecated)")
    code_size: int = Field(..., description="Size of generated code in bytes")
    dependencies: List[str] = Field(default_factory=list, description="Python package dependencies")
    validation_passed: bool = Field(default=False, description="Whether validation passed")
    deployment_status: Optional[str] = Field(None, description="Deployment status")

    # CrewAI specific fields
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Tool input schema")
    has_config_params: bool = Field(default=False, description="Whether tool has config parameters")
    requirements: List[str] = Field(default_factory=list, description="Functional requirements")


class ToolRegistrationRequest(BaseModel):
    """Request to register a generated tool"""
    name: str
    display_name: str
    description: str
    category: str
    platform: str = "crewai"
    version: str = "1.0.0"
    author: str
    code_size: int
    dependencies: List[str] = []
    validation_passed: bool = False
    deployment_status: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    has_config_params: bool = False
    requirements: List[str] = []


class ToolListResponse(BaseModel):
    """Response for tool list"""
    total: int
    tools: List[ToolMetadata]
