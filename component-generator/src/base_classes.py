"""
Base classes and models for CrewAI Tool Generator
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod


class ToolSpec(BaseModel):
    """Specification for a crewAI tool to be generated"""
    name: str = Field(..., description="Tool class name (PascalCase, e.g., 'CustomApiTool')")
    display_name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="What the tool does")
    category: str = Field(..., description="Tool category (api, search, file, database, custom)")
    platforms: List[str] = Field(default=["crewai"], description="Target platforms")

    requirements: List[str] = Field(default_factory=list, description="Functional requirements")

    inputs: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Input parameters for the tool"
    )

    config_params: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional configuration parameters for __init__"
    )

    dependencies: List[str] = Field(
        default_factory=list,
        description="Python package dependencies (e.g., ['requests', 'beautifulsoup4'])"
    )

    author: str = Field(default="Component Factory", description="Tool author")
    version: str = Field(default="1.0.0", description="Tool version")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "CustomApiTool",
                "display_name": "API Caller",
                "description": "Make HTTP API calls with custom parameters",
                "category": "api",
                "platforms": ["crewai"],
                "requirements": [
                    "Support GET, POST, PUT, DELETE methods",
                    "Accept custom headers and query parameters"
                ],
                "inputs": [
                    {
                        "name": "endpoint",
                        "type": "str",
                        "description": "API endpoint path",
                        "required": True
                    }
                ],
                "dependencies": ["requests"],
                "author": "Your Name",
                "version": "1.0.0"
            }
        }


class ValidationResult(BaseModel):
    """Result of code validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class GeneratedTool(BaseModel):
    """Generated tool component with metadata"""
    tool_code: str = Field(..., description="Generated Python code")
    tool_config: Dict[str, Any] = Field(default_factory=dict, description="Tool configuration metadata")
    dependencies: List[str] = Field(default_factory=list)
    validation: ValidationResult
    documentation: Optional[str] = Field(None, description="Usage documentation")
    deployment_instructions: Optional[Dict[str, Any]] = Field(None)


class FeasibilityAssessment(BaseModel):
    """Assessment of generation feasibility"""
    feasible: bool
    confidence: str = Field(..., description="Confidence level: high, medium, low, blocked")
    complexity: str = Field(..., description="Complexity: simple, medium, complex")
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)
    similar_patterns_found: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()


class BaseCodeGenerator(ABC):
    """Abstract base class for code generators"""

    @abstractmethod
    async def generate_tool(self, spec: ToolSpec) -> GeneratedTool:
        """Generate tool code from specification"""
        pass

    @abstractmethod
    async def validate_tool(self, code: str) -> ValidationResult:
        """Validate generated tool code"""
        pass
