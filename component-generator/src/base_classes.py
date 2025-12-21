"""
Base classes and models for CrewAI Tool Generator
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from abc import ABC, abstractmethod


class ToolInputParameter(BaseModel):
    """
    Structured input parameter definition with validation

    Supports both simple and complex types with proper Field descriptions
    """
    name: str = Field(..., description="Parameter name (snake_case)")
    type: str = Field(
        ...,
        description="Python type hint (e.g., 'str', 'int', 'List[str]', 'Dict[str, Any]', 'Optional[bool]')"
    )
    description: str = Field(
        ...,
        description="Clear description of what this parameter does (minimum 10 characters)"
    )
    required: bool = Field(
        default=True,
        description="Whether this parameter is required (True) or optional (False)"
    )
    default_value: Optional[Any] = Field(
        default=None,
        description="Default value for optional parameters (None if required=True)"
    )
    param_kind: Literal["runtime", "config"] = Field(
        default="runtime",
        description="'runtime' for _run() parameters, 'config' for __init__() parameters"
    )
    examples: Optional[List[str]] = Field(
        default=None,
        description="Example values for documentation"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate parameter name follows Python conventions"""
        import re
        if not re.match(r'^[a-z][a-z0-9_]*$', v):
            # Generate suggestion for fixing the name
            suggestion = re.sub(r'([A-Z]+)', r'_\1', v).lower().lstrip('_')
            suggestion = re.sub(r'[^a-z0-9_]', '_', suggestion)
            suggestion = re.sub(r'_+', '_', suggestion).strip('_')

            raise ValueError(
                f"Invalid parameter name: '{v}'\n"
                f"  ✗ Parameter names must be snake_case (lowercase with underscores)\n"
                f"  ✓ Suggested fix: '{suggestion}'\n"
                f"  ℹ Valid examples: 'api_key', 'max_retries', 'timeout_seconds'"
            )
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description quality"""
        # Check minimum character length first
        if len(v) < 10:
            word_count = len(v.split())
            raise ValueError(
                f"Description too short: '{v}' ({len(v)} characters, {word_count} word{'s' if word_count != 1 else ''})\n"
                f"  ✗ Must be at least 10 characters to be meaningful\n"
                f"  ✓ Example: 'API key for authentication' (28 characters)\n"
                f"  ✓ Example: 'Maximum number of retry attempts' (36 characters)\n"
                f"  ✓ Example: 'Timeout duration in seconds' (28 characters)"
            )

        word_count = len(v.split())

        if word_count < 3:
            raise ValueError(
                f"Description too short: '{v}' ({word_count} word{'s' if word_count != 1 else ''})\n"
                f"  ✗ Must contain at least 3 words to be meaningful\n"
                f"  ✓ Example: 'API key for authentication'\n"
                f"  ✓ Example: 'Maximum number of retry attempts'\n"
                f"  ✓ Example: 'Timeout duration in seconds'"
            )

        if v.lower() == v:
            # Suggest proper capitalization
            suggestion = v[0].upper() + v[1:] if len(v) > 1 else v.upper()
            raise ValueError(
                f"Description needs proper capitalization: '{v}'\n"
                f"  ✗ All lowercase is not recommended\n"
                f"  ✓ Suggested fix: '{suggestion}'\n"
                f"  ℹ Start with a capital letter for better readability"
            )

        if v.upper() == v:
            # Suggest proper capitalization
            suggestion = v.capitalize()
            raise ValueError(
                f"Description needs proper capitalization: '{v}'\n"
                f"  ✗ All uppercase is not recommended\n"
                f"  ✓ Suggested fix: '{suggestion}'\n"
                f"  ℹ Use normal sentence case"
            )

        return v

    @model_validator(mode='after')
    def validate_required_default(self):
        """Validate that required parameters don't have defaults"""
        if self.required and self.default_value is not None:
            raise ValueError(
                f"Conflicting configuration for parameter '{self.name}'\n"
                f"  ✗ Cannot be both required=True and have a default_value\n"
                f"  ✓ Fix option 1: Set required=False (keep default_value={repr(self.default_value)})\n"
                f"  ✓ Fix option 2: Set required=True (remove default_value)\n"
                f"  ℹ Required parameters cannot have defaults - users must always provide them"
            )

        if not self.required and self.default_value is None and self.param_kind == "runtime":
            # For optional runtime parameters, suggest a default based on type
            type_defaults = {
                'str': '""',
                'int': '0',
                'float': '0.0',
                'bool': 'False',
                'List[str]': '[]',
                'List[int]': '[]',
                'Dict[str, Any]': '{}',
            }
            suggested_default = type_defaults.get(self.type, 'None')

            raise ValueError(
                f"Missing default value for optional parameter '{self.name}'\n"
                f"  ✗ Optional runtime parameters must have a default_value\n"
                f"  ✓ Suggested: default_value={suggested_default}\n"
                f"  ℹ Type: {self.type}\n"
                f"  ℹ Note: Config parameters can use None, but runtime parameters need explicit defaults"
            )
        return self

    @field_validator('type')
    @classmethod
    def validate_type_hint(cls, v: str) -> str:
        """Validate type hint is a valid Python type"""
        valid_simple_types = {'str', 'int', 'float', 'bool', 'bytes', 'Any'}
        valid_complex_prefixes = {'List', 'Dict', 'Optional', 'Union', 'Tuple', 'Set'}

        # Check if it's a simple type
        if v in valid_simple_types:
            return v

        # Check if it's a complex type
        for prefix in valid_complex_prefixes:
            if v.startswith(prefix + '['):
                return v

        # Allow custom types (could be imported classes)
        if v and v[0].isupper():
            return v

        # Generate helpful suggestion
        suggestion = None
        v_lower = v.lower()

        # Common mistakes and suggestions
        if v_lower == 'list':
            suggestion = 'List[str]  # or List[int], List[Dict[str, Any]], etc.'
        elif v_lower == 'dict':
            suggestion = 'Dict[str, Any]  # or Dict[str, str], etc.'
        elif v_lower in ('optional', 'option'):
            suggestion = 'Optional[str]  # or Optional[int], etc.'
        elif v_lower == 'string':
            suggestion = 'str'
        elif v_lower == 'integer':
            suggestion = 'int'
        elif v_lower == 'boolean':
            suggestion = 'bool'

        error_msg = f"Invalid type hint: '{v}'\n"
        error_msg += f"  ✗ Not a recognized Python type\n"

        if suggestion:
            error_msg += f"  ✓ Did you mean: {suggestion}\n"

        error_msg += f"  ℹ Simple types: {', '.join(sorted(valid_simple_types))}\n"
        error_msg += f"  ℹ Complex types: {', '.join(p + '[...]' for p in sorted(valid_complex_prefixes))}\n"
        error_msg += f"  ℹ Examples:\n"
        error_msg += f"    - List[str] for a list of strings\n"
        error_msg += f"    - Dict[str, Any] for a dictionary\n"
        error_msg += f"    - Optional[int] for an optional integer\n"
        error_msg += f"    - Union[str, int] for multiple allowed types"

        raise ValueError(error_msg)

    def to_field_definition(self) -> str:
        """
        Generate Pydantic Field definition for this parameter

        Returns:
            String like: 'param_name: str = Field(..., description="...")'
        """
        field_args = [f'description="{self.description}"']

        if not self.required:
            if self.default_value is not None:
                # Format default value properly
                if isinstance(self.default_value, str):
                    default = f'"{self.default_value}"'
                elif isinstance(self.default_value, bool):
                    default = str(self.default_value)
                elif self.default_value is None:
                    default = 'None'
                else:
                    default = repr(self.default_value)
            else:
                default = 'None'

            return f'{self.name}: {self.type} = Field({default}, {", ".join(field_args)})'
        else:
            return f'{self.name}: {self.type} = Field(..., {", ".join(field_args)})'

    def get_type_imports(self) -> List[str]:
        """
        Get required imports for this type

        Returns:
            List of import statements needed
        """
        imports = []

        # Check for complex types
        if 'List[' in self.type and 'from typing import List' not in imports:
            imports.append('List')
        if 'Dict[' in self.type and 'from typing import Dict' not in imports:
            imports.append('Dict')
        if 'Optional[' in self.type and 'from typing import Optional' not in imports:
            imports.append('Optional')
        if 'Union[' in self.type and 'from typing import Union' not in imports:
            imports.append('Union')
        if 'Tuple[' in self.type and 'from typing import Tuple' not in imports:
            imports.append('Tuple')
        if 'Set[' in self.type and 'from typing import Set' not in imports:
            imports.append('Set')
        if 'Any' in self.type and 'from typing import Any' not in imports:
            imports.append('Any')

        return imports


class ToolSpec(BaseModel):
    """Specification for a crewAI tool to be generated"""
    name: str = Field(..., description="Tool class name (PascalCase, e.g., 'CustomApiTool')")
    display_name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="What the tool does")
    category: str = Field(..., description="Tool category (api, search, file, database, custom)")
    platforms: List[str] = Field(default=["crewai"], description="Target platforms")

    requirements: List[str] = Field(default_factory=list, description="Functional requirements")

    # Support both old Dict format and new ToolInputParameter format for backwards compatibility
    inputs: Union[List[Dict[str, Any]], List[ToolInputParameter]] = Field(
        default_factory=list,
        description="Input parameters for the tool (runtime parameters for _run())"
    )

    config_params: Optional[Union[List[Dict[str, Any]], List[ToolInputParameter]]] = Field(
        default=None,
        description="Optional configuration parameters for __init__ (config parameters)"
    )

    dependencies: List[str] = Field(
        default_factory=list,
        description="Python package dependencies (e.g., ['requests', 'beautifulsoup4'])"
    )

    author: str = Field(default="Component Factory", description="Tool author")
    version: str = Field(default="1.0.0", description="Tool version")

    def get_normalized_inputs(self) -> List[ToolInputParameter]:
        """
        Get inputs as ToolInputParameter objects

        Converts Dict format to ToolInputParameter for backwards compatibility
        """
        if not self.inputs:
            return []

        normalized = []
        for inp in self.inputs:
            if isinstance(inp, ToolInputParameter):
                normalized.append(inp)
            else:
                # Convert Dict to ToolInputParameter
                normalized.append(ToolInputParameter(
                    name=inp['name'],
                    type=inp.get('type', 'str'),
                    description=inp.get('description', f"Parameter {inp['name']}"),
                    required=inp.get('required', True),
                    default_value=inp.get('default_value'),
                    param_kind="runtime",
                    examples=inp.get('examples')
                ))
        return normalized

    def get_normalized_config_params(self) -> List[ToolInputParameter]:
        """
        Get config_params as ToolInputParameter objects

        Converts Dict format to ToolInputParameter for backwards compatibility
        """
        if not self.config_params:
            return []

        normalized = []
        for param in self.config_params:
            if isinstance(param, ToolInputParameter):
                normalized.append(param)
            else:
                # Convert Dict to ToolInputParameter
                normalized.append(ToolInputParameter(
                    name=param['name'],
                    type=param.get('type', 'str'),
                    description=param.get('description', f"Config parameter {param['name']}"),
                    required=param.get('required', False),
                    default_value=param.get('default_value'),
                    param_kind="config",
                    examples=param.get('examples')
                ))
        return normalized

    def get_all_type_imports(self) -> List[str]:
        """
        Get all required typing imports from all parameters

        Returns:
            List of unique import names (e.g., ['List', 'Dict', 'Optional'])
        """
        imports = set()

        # Collect from inputs
        for inp in self.get_normalized_inputs():
            imports.update(inp.get_type_imports())

        # Collect from config params
        for param in self.get_normalized_config_params():
            imports.update(param.get_type_imports())

        return sorted(list(imports))

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
                        "description": "API endpoint URL to call",
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
