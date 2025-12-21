"""
CrewAI Tool Generator using Claude AI
"""

import os
import json
import yaml
import re
from typing import Optional, Dict, Any
import structlog
from anthropic import Anthropic

from base_classes import (
    ToolSpec,
    GeneratedTool,
    ValidationResult,
    BaseCodeGenerator
)
from crewai_validator import CrewAIToolValidator
from dependency_validator import DependencyValidator, get_validation_summary
from pattern_matcher import PatternMatcher, get_pattern_report
from test_generator import TestFileGenerator

logger = structlog.get_logger()


class CrewAIToolGenerator(BaseCodeGenerator):
    """Generates crewAI tool code using Claude AI"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        rag_service_url: Optional[str] = None,
        max_retries: int = 2
    ):
        """
        Initialize the generator

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
            rag_service_url: URL of RAG service for pattern matching (optional)
            max_retries: Maximum number of retry attempts with fixes
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required (set ANTHROPIC_API_KEY env var)")

        self.model = model
        self.rag_service_url = rag_service_url or os.getenv("RAG_SERVICE_URL")
        self.max_retries = max_retries

        self.client = Anthropic(api_key=self.api_key)
        self.validator = CrewAIToolValidator()
        self.dependency_validator = DependencyValidator()
        self.pattern_matcher = PatternMatcher()
        self.test_generator = TestFileGenerator()
        self.logger = logger.bind(component="crewai_generator")

        # Load manual implementation templates
        self.manual_implementations = self._load_manual_implementations()

    def _load_manual_implementations(self) -> Dict[str, Any]:
        """Load manual implementation templates from YAML file"""
        try:
            templates_path = os.path.join(
                os.path.dirname(__file__),
                'manual_implementations.yaml'
            )

            if not os.path.exists(templates_path):
                self.logger.warning(
                    "Manual implementations file not found",
                    path=templates_path
                )
                return {}

            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)

            self.logger.info(
                "Manual implementation templates loaded",
                patterns_count=len(templates.get('patterns', {}))
            )

            return templates

        except Exception as e:
            self.logger.error(
                "Failed to load manual implementations",
                error=str(e)
            )
            return {}

    def _get_manual_implementation_templates(self, unsupported_deps: list) -> str:
        """
        Get relevant code templates for unsupported dependencies

        Args:
            unsupported_deps: List of unsupported dependency names

        Returns:
            Formatted string with code templates and guidelines
        """
        if not self.manual_implementations or not unsupported_deps:
            return ""

        templates_text = ""
        patterns_data = self.manual_implementations.get('patterns', {})
        added_patterns = set()

        for dep in unsupported_deps:
            # Get pattern guide
            guide = self.dependency_validator.get_manual_implementation_guide(dep)
            pattern_name = guide['pattern']

            # Skip if we've already added this pattern
            if pattern_name in added_patterns:
                continue

            # Get pattern data from templates
            pattern_data = patterns_data.get(pattern_name)

            if pattern_data:
                templates_text += f"\n**📘 Code Templates for '{pattern_name}' Pattern:**\n"
                templates_text += f"**Use Case:** {pattern_data.get('description', 'N/A')}\n"
                templates_text += f"**Stdlib Modules:** {', '.join(pattern_data.get('stdlib_modules', []))}\n\n"

                # Add code examples
                examples = pattern_data.get('examples', [])
                for i, example in enumerate(examples[:2], 1):  # Limit to 2 examples per pattern
                    templates_text += f"**Example {i}: {example.get('name', 'N/A')}**\n"
                    templates_text += f"_{example.get('description', '')}_\n\n"
                    templates_text += "```python\n"
                    templates_text += example.get('code', '').strip()
                    templates_text += "\n```\n\n"

                added_patterns.add(pattern_name)
            else:
                # Fallback to basic guide info
                templates_text += f"\n**Manual Implementation for '{dep}':**\n"
                templates_text += f"- Pattern: {guide['pattern']}\n"
                templates_text += f"- Description: {guide['description']}\n"
                templates_text += f"- Recommended stdlib modules: {', '.join(guide['recommended_stdlib'])}\n"
                templates_text += f"- Approach: {guide['implementation_approach']}\n\n"

        # Add integration guidelines if available
        if templates_text and self.manual_implementations.get('integration_guidelines'):
            templates_text += "\n**🎯 Integration Guidelines:**\n"
            templates_text += self.manual_implementations['integration_guidelines'].strip()
            templates_text += "\n\n"

        return templates_text

    async def generate_tool(self, spec: ToolSpec) -> GeneratedTool:
        """
        Generate crewAI tool code from specification

        Args:
            spec: Tool specification

        Returns:
            GeneratedTool with code and validation results
        """
        self.logger.info("Starting tool generation", tool_name=spec.name)

        # 1. Validate dependencies
        self.logger.info("=" * 80)
        self.logger.info("Validating dependencies...")
        self.logger.info("=" * 80)
        dependency_validation = self.dependency_validator.validate(
            spec.dependencies if spec.dependencies else []
        )

        # Log validation summary
        validation_summary = get_validation_summary(dependency_validation)
        self.logger.info(
            "Dependency validation completed",
            total_dependencies=len(dependency_validation.supported) + len(dependency_validation.unsupported),
            supported_count=len(dependency_validation.supported),
            unsupported_count=len(dependency_validation.unsupported),
            stdlib_count=len(dependency_validation.stdlib),
            external_count=len(dependency_validation.external),
            severity=dependency_validation.severity,
            manual_implementation_needed=dependency_validation.manual_implementation_needed
        )
        print(validation_summary)  # Print to console for visibility

        # Log individual warnings
        if dependency_validation.warnings:
            self.logger.warning("Dependency validation warnings detected")
            for warning in dependency_validation.warnings:
                self.logger.warning("Dependency warning", message=warning)

        # Log suggestions
        if dependency_validation.suggestions:
            self.logger.info("Dependency validation suggestions available")
            for suggestion in dependency_validation.suggestions:
                self.logger.info("Dependency suggestion", message=suggestion)

        # Check if we can proceed
        if not dependency_validation.can_proceed:
            self.logger.error(
                "Cannot proceed with unsupported dependencies in strict mode",
                unsupported=dependency_validation.unsupported
            )
            raise ValueError(
                f"Unsupported dependencies: {', '.join(dependency_validation.unsupported)}"
            )

        # 2. Retrieve similar patterns from RAG (if available)
        rag_context = await self._retrieve_similar_components(spec)

        # 3. Generate code using Claude
        generated_code = None
        validation_result = None
        attempt = 0

        while attempt <= self.max_retries:
            attempt += 1

            self.logger.info(f"Generation attempt {attempt}/{self.max_retries + 1}")

            # Generate code
            generated_code = await self._generate_code_with_claude(
                spec,
                rag_context,
                dependency_validation=dependency_validation,
                previous_errors=validation_result.errors if validation_result else None
            )

            # Validate generated code
            validation_result = await self.validate_tool(generated_code)

            if validation_result.is_valid:
                self.logger.info("Tool generated successfully", tool_name=spec.name)

                # Log the generated code to console (like Flowise)
                self.logger.info("=" * 80)
                self.logger.info(f"Generated {spec.name}.py:")
                self.logger.info("=" * 80)
                print(generated_code)  # Print to stdout for docker logs
                print("=" * 80)

                # Save generated code to local file for testing
                self._save_generated_tool_to_file(spec.name, generated_code)

                break

            self.logger.warning(
                f"Validation failed (attempt {attempt})",
                errors=validation_result.errors
            )

            if attempt > self.max_retries:
                self.logger.error("Max retries exceeded", tool_name=spec.name)
                break

        # 3. Generate documentation
        self.logger.info("=" * 80)
        self.logger.info("Generating documentation...")
        self.logger.info("=" * 80)
        documentation = self._generate_documentation(spec, generated_code)
        self.logger.info(
            "Documentation generated successfully",
            tool_name=spec.name,
            doc_size=len(documentation)
        )

        # 4. Create deployment instructions with dependency validation
        deployment_instructions = {
            "usage": f"from generated_tools.{spec.name.lower()} import {spec.name}",
            "dependencies": spec.dependencies,
            "install_command": f"pip install {' '.join(spec.dependencies)}" if spec.dependencies else None,
            "dependency_validation": dependency_validation.to_dict()
        }

        # Add warnings if dependencies are unsupported
        if dependency_validation.unsupported:
            deployment_instructions["warnings"] = dependency_validation.warnings
            deployment_instructions["manual_implementation_note"] = (
                "Some dependencies are not supported in CrewAI-Studio. "
                "The generated code uses manual implementations with Python stdlib."
            )

        # 5. Create the complete response object
        generated_tool = GeneratedTool(
            tool_code=generated_code,
            tool_config={
                "name": spec.name,
                "display_name": spec.display_name,
                "category": spec.category,
                "version": spec.version,
                "author": spec.author
            },
            dependencies=spec.dependencies,
            validation=validation_result,
            documentation=documentation,
            deployment_instructions=deployment_instructions
        )

        # 6. Save complete JSON response to file (like Flowise)
        self._save_generation_response_to_json(spec.name, generated_tool)

        # 7. Generate and save test file for the tool
        self._generate_test_file(spec, generated_code)

        return generated_tool

    async def _retrieve_similar_components(self, spec: ToolSpec) -> Dict[str, Any]:
        """Retrieve similar tool patterns from RAG service"""
        if not self.rag_service_url:
            self.logger.info("RAG service not configured, skipping pattern retrieval")
            return {"results": []}

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_service_url}/api/crewai/patterns/similar",
                    json={
                        "description": spec.description,
                        "category": spec.category,
                        "n_results": 3
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(
                        "Retrieved similar patterns",
                        count=data.get('results_count', 0)
                    )
                    return data

        except Exception as e:
            self.logger.warning("Failed to retrieve patterns from RAG", error=str(e))

        return {"results": []}

    async def _generate_code_with_claude(
        self,
        spec: ToolSpec,
        rag_context: Dict[str, Any],
        dependency_validation,
        previous_errors: Optional[list] = None
    ) -> str:
        """Generate tool code using Claude AI"""

        # Build the prompt
        prompt = self._build_generation_prompt(
            spec,
            rag_context,
            dependency_validation,
            previous_errors
        )

        self.logger.debug("Sending request to Claude", model=self.model)

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract code from response
            response_text = message.content[0].text

            # Extract Python code from markdown code blocks if present
            code = self._extract_code_from_response(response_text)

            return code

        except Exception as e:
            self.logger.error("Claude API call failed", error=str(e))
            raise

    def _build_generation_prompt(
        self,
        spec: ToolSpec,
        rag_context: Dict[str, Any],
        dependency_validation,
        previous_errors: Optional[list] = None
    ) -> str:
        """Build the prompt for Claude"""

        prompt = f"""You are an expert Python developer specializing in crewAI framework. Generate a complete, production-ready crewAI tool based on the following specification.

# Tool Specification

**Name:** {spec.name}
**Display Name:** {spec.display_name}
**Description:** {spec.description}
**Category:** {spec.category}

## Requirements
"""

        for req in spec.requirements:
            prompt += f"- {req}\n"

        # Use normalized parameter objects for enhanced type support
        runtime_params = spec.get_normalized_inputs()
        config_params = spec.get_normalized_config_params()

        if runtime_params:
            prompt += "\n## Input Parameters (Runtime - for _run method)\n"
            for param in runtime_params:
                required = "**required**" if param.required else "*optional*"
                default_info = f" (default: {param.default_value})" if param.default_value is not None else ""
                prompt += f"- **{param.name}** (`{param.type}`, {required}){default_info}: {param.description}\n"
                if param.examples:
                    prompt += f"  - Examples: {', '.join(str(e) for e in param.examples)}\n"

        if config_params:
            prompt += "\n## Configuration Parameters (Config - for __init__ method)\n"
            for param in config_params:
                default_info = f" (default: {param.default_value})" if param.default_value is not None else ""
                prompt += f"- **{param.name}** (`{param.type}`){default_info}: {param.description}\n"
                if param.examples:
                    prompt += f"  - Examples: {', '.join(str(e) for e in param.examples)}\n"

        # Add dependency validation information
        if spec.dependencies:
            prompt += "\n## Dependencies & Validation\n"

            if dependency_validation.all_supported:
                prompt += "✅ **All dependencies are supported in CrewAI-Studio environment:**\n"
                for dep in dependency_validation.supported:
                    if dep in dependency_validation.stdlib:
                        prompt += f"- {dep} (Python stdlib - always available)\n"
                    else:
                        prompt += f"- {dep} (supported)\n"
            else:
                prompt += "⚠️ **Dependency Validation Results:**\n\n"

                if dependency_validation.supported:
                    prompt += "**✅ Supported (you can use these):**\n"
                    for dep in dependency_validation.supported:
                        if dep in dependency_validation.stdlib:
                            prompt += f"- {dep} (Python stdlib)\n"
                        else:
                            prompt += f"- {dep}\n"
                    prompt += "\n"

                if dependency_validation.unsupported:
                    prompt += "**❌ Unsupported (DO NOT import these directly):**\n"
                    for dep in dependency_validation.unsupported:
                        prompt += f"- {dep}\n"
                        alts = dependency_validation.alternatives.get(dep, [])
                        if alts:
                            prompt += f"  → Alternatives: {', '.join(alts)}\n"
                    prompt += "\n"

                    prompt += "**🔧 IMPORTANT - Manual Implementation Required:**\n"
                    prompt += "For unsupported dependencies, you MUST implement the functionality manually "
                    prompt += "using ONLY Python standard library (stdlib) modules.\n\n"
                    prompt += "**Manual Implementation Guidelines:**\n"
                    prompt += "1. Use ONLY Python stdlib modules (os, json, datetime, urllib, http.client, etc.)\n"
                    prompt += "2. Do NOT import any unsupported libraries\n"
                    prompt += "3. Keep implementations simple and focused\n"
                    prompt += "4. Add clear docstrings explaining the manual implementation\n"
                    prompt += "5. Include proper error handling\n\n"

                    # Add code templates for unsupported dependencies
                    prompt += self._get_manual_implementation_templates(
                        dependency_validation.unsupported
                    )

            # Add warnings and suggestions
            if dependency_validation.warnings:
                prompt += "\n**⚠️ Warnings:**\n"
                for warning in dependency_validation.warnings:
                    prompt += f"- {warning}\n"

            if dependency_validation.suggestions:
                prompt += "\n**💡 Suggestions:**\n"
                for suggestion in dependency_validation.suggestions:
                    prompt += f"- {suggestion}\n"

            prompt += "\n"

        # Add similar patterns if available
        if rag_context.get('results'):
            prompt += "\n## Similar Tool Patterns (for reference)\n"
            for i, pattern in enumerate(rag_context['results'][:2], 1):
                prompt += f"\n### Pattern {i}: {pattern.get('name', 'Unknown')}\n"
                prompt += f"```python\n{pattern.get('code', '')[:500]}...\n```\n"

        # Add error feedback if retrying
        if previous_errors:
            prompt += "\n## Previous Generation Errors (FIX THESE)\n"
            for error in previous_errors:
                prompt += f"- {error}\n"

        # Generate proper typing imports based on actual parameter types
        typing_imports = spec.get_all_type_imports()
        if not typing_imports:
            typing_imports = ['Optional', 'Dict', 'Any']  # Defaults

        # Always include Type for args_schema
        if 'Type' not in typing_imports:
            typing_imports.append('Type')

        typing_imports_str = ', '.join(sorted(typing_imports))

        prompt += f"""

# Code Generation Instructions

Generate a complete crewAI tool following this **exact structure**:

```python
from typing import {typing_imports_str}
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# 1. Input Schema (if tool has parameters)
class {{ToolName}}InputSchema(BaseModel):
    \"\"\"Input schema for {{ToolName}}\"\"\"
    # Use exact Field definitions from parameter specs
    # Example: param_name: str = Field(..., description="Description here")
    # Example with optional: param_name: Optional[int] = Field(None, description="Optional param")
    # Example with List: items: List[str] = Field(..., description="List of items")
    # Example with Dict: config: Dict[str, Any] = Field(..., description="Configuration dict")

# 2. Main Tool Class
class {{ToolName}}(BaseTool):
    name: str = "{{display_name}}"
    description: str = "{{description}}"
    args_schema: Type[BaseModel] = {{ToolName}}InputSchema

    # Configuration parameters (if needed)
    config_param: Optional[str] = None

    def __init__(self, config_param: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.config_param = config_param

    def _run(self, param1: str, param2: Optional[int] = None) -> Any:
        \"\"\"
        Implementation of the tool logic

        Args:
            param1: Description
            param2: Description

        Returns:
            Tool output
        \"\"\"
        try:
            # Implementation here
            result = None  # Your logic
            return result
        except Exception as e:
            return {{"error": str(e)}}
```

# Important Requirements - FOLLOW OFFICIAL CrewAI TEMPLATE

1. **Use the EXACT class name from spec:** `{spec.name}`
2. **Include proper type hints** (from typing module)
3. **Create InputSchema** if tool has parameters
4. **Implement ONLY the _run() method** - BaseTool handles run()
5. **DO NOT add a run() method** - This breaks compatibility
6. **DO NOT call _generate_description()** - BaseTool handles this
7. **Add comprehensive docstrings**
8. **Include error handling** in _run()
9. **Return structured data** (dict or string)
10. **Follow official CrewAI BaseTool template exactly**

# Code Quality

- Clean, readable code
- Proper error handling
- Type annotations
- Comprehensive docstrings
- Follow PEP 8 style guide

Generate **ONLY the Python code**, no explanations. Start directly with imports.
"""

        return prompt

    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from Claude's response"""
        import re

        # Try to extract code from markdown code blocks
        code_block_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks, try to find Python code directly
        # Look for imports as start marker
        if 'import' in response or 'from' in response:
            # Try to extract everything from first import
            lines = response.split('\n')
            code_lines = []
            started = False

            for line in lines:
                if 'import' in line or 'from' in line:
                    started = True

                if started:
                    code_lines.append(line)

            if code_lines:
                return '\n'.join(code_lines).strip()

        # Fallback: return as-is
        return response.strip()

    async def validate_tool(self, code: str) -> ValidationResult:
        """Validate generated tool code with AST and pattern matching"""
        # Run AST validation
        ast_validation = self.validator.validate(code)

        # Run pattern matching
        pattern_result = self.pattern_matcher.analyze(code)

        # Log pattern matching results
        self.logger.info(
            "Pattern validation completed",
            matches_pattern=pattern_result.matches_pattern,
            pattern_score=pattern_result.pattern_score
        )

        # Print pattern report to console
        pattern_report = get_pattern_report(pattern_result)
        print("\n" + pattern_report)

        # Combine validations - tool is valid if both pass
        combined_errors = ast_validation.errors.copy()
        combined_warnings = ast_validation.warnings.copy()
        combined_suggestions = ast_validation.suggestions.copy()

        # Add pattern matching issues
        if pattern_result.issues:
            combined_errors.extend(pattern_result.issues)
        if pattern_result.warnings:
            combined_warnings.extend(pattern_result.warnings)
        if pattern_result.suggestions:
            combined_suggestions.extend(pattern_result.suggestions)

        # Tool is valid if AST is valid AND pattern score >= 70
        is_valid = ast_validation.is_valid and pattern_result.pattern_score >= 70

        # Create enhanced validation result
        return ValidationResult(
            is_valid=is_valid,
            errors=combined_errors,
            warnings=combined_warnings,
            suggestions=combined_suggestions
        )

    def _generate_documentation(self, spec: ToolSpec, code: str) -> str:
        """Generate usage documentation for the tool"""

        doc = f"""# {spec.display_name}

**Version:** {spec.version}
**Author:** {spec.author}
**Category:** {spec.category}

## Description

{spec.description}

## Installation

```bash
pip install crewai"""

        if spec.dependencies:
            doc += f" {' '.join(spec.dependencies)}"

        doc += """
```

## Usage

```python
from crewai import Agent, Task, Crew
from {tool_module} import {tool_class}

# Initialize the tool
tool = {tool_class}()

# Create an agent with the tool
agent = Agent(
    role='Assistant',
    goal='Help with tasks',
    backstory='Helpful assistant',
    tools=[tool],
    verbose=True
)

# Create and run a task
task = Task(
    description='Task description here',
    agent=agent,
    expected_output='Expected output'
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

## Parameters

""".format(
            tool_module=spec.name.lower(),
            tool_class=spec.name
        )

        # Use normalized parameters for documentation
        runtime_params = spec.get_normalized_inputs()
        for param in runtime_params:
            required = "**Required**" if param.required else "*Optional*"
            default_str = f" (default: `{param.default_value}`)" if param.default_value is not None else ""
            doc += f"- **{param.name}** (`{param.type}`) - {required}{default_str}: {param.description}\n"
            if param.examples:
                doc += f"  - Examples: {', '.join(f'`{e}`' for e in param.examples)}\n"

        config_params = spec.get_normalized_config_params()
        if config_params:
            doc += "\n## Configuration\n\n"
            for param in config_params:
                default_str = f" (default: `{param.default_value}`)" if param.default_value is not None else ""
                doc += f"- **{param.name}** (`{param.type}`){default_str}: {param.description}\n"
                if param.examples:
                    doc += f"  - Examples: {', '.join(f'`{e}`' for e in param.examples)}\n"

        doc += """
## Requirements

"""
        for req in spec.requirements:
            doc += f"- {req}\n"

        return doc

    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase/camelCase to snake_case"""
        import re
        # Insert underscore before capital letters (except first) and convert to lowercase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _save_generated_tool_to_file(self, tool_name: str, code: str):
        """
        Save generated tool code to local file for testing and reference

        Args:
            tool_name: Name of the tool (PascalCase)
            code: Generated Python code
        """
        try:
            # Create generated_tools directory if it doesn't exist
            output_dir = os.path.join("/app/data", "generated_tools")
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename using snake_case (official Python/CrewAI convention)
            snake_case_name = self._to_snake_case(tool_name)
            filename = f"{snake_case_name}.py"
            filepath = os.path.join(output_dir, filename)

            # Write code to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)

            self.logger.info(
                "Generated tool saved to file",
                tool_name=tool_name,
                filename=filename,
                filepath=filepath,
                file_size=len(code)
            )

            # Update __init__.py to export this tool
            self._update_tools_init_file(output_dir, tool_name, snake_case_name)

        except Exception as e:
            self.logger.warning(
                "Failed to save generated tool to file",
                tool_name=tool_name,
                error=str(e)
            )

    def _update_tools_init_file(self, output_dir: str, class_name: str, module_name: str):
        """
        Update or create __init__.py in the tools directory to export generated tools

        Args:
            output_dir: Directory containing the generated tools
            class_name: Tool class name (PascalCase)
            module_name: Module filename without .py (snake_case)
        """
        try:
            init_file_path = os.path.join(output_dir, "__init__.py")

            # Read existing __init__.py or create new content
            existing_imports = []
            existing_exports = []

            if os.path.exists(init_file_path):
                with open(init_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Parse existing imports
                    import_pattern = r'from \.(\w+) import (\w+)'
                    existing_imports = re.findall(import_pattern, content)

                    # Parse existing exports
                    all_pattern = r'__all__\s*=\s*\[(.*?)\]'
                    all_match = re.search(all_pattern, content, re.DOTALL)
                    if all_match:
                        exports_str = all_match.group(1)
                        existing_exports = [e.strip(' "\',\n') for e in exports_str.split(',') if e.strip()]

            # Add new tool if not already present
            new_import = (module_name, class_name)
            if new_import not in existing_imports:
                existing_imports.append(new_import)

            if class_name not in existing_exports:
                existing_exports.append(class_name)

            # Generate new __init__.py content
            init_content = "# Auto-generated file - exports all generated CrewAI tools\n\n"

            # Add imports
            for module, class_name_entry in sorted(existing_imports):
                init_content += f"from .{module} import {class_name_entry}\n"

            # Add __all__
            init_content += "\n__all__ = [\n"
            for export in sorted(existing_exports):
                init_content += f'    "{export}",\n'
            init_content += "]\n"

            # Write updated __init__.py
            with open(init_file_path, 'w', encoding='utf-8') as f:
                f.write(init_content)

            self.logger.info(
                "__init__.py updated",
                path=init_file_path,
                exported_tools=len(existing_exports)
            )

        except Exception as e:
            self.logger.warning(
                "Failed to update __init__.py",
                error=str(e)
            )

    def _save_generation_response_to_json(self, tool_name: str, generated_tool):
        """
        Save complete generation response to JSON file (like Flowise)

        Args:
            tool_name: Name of the tool
            generated_tool: GeneratedTool object with complete response
        """
        try:
            import json
            from datetime import datetime

            # Create generated_tools directory if it doesn't exist
            output_dir = os.path.join("/app/data", "generated_tools")
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{tool_name}_response.json"
            filepath = os.path.join(output_dir, filename)

            # Convert to dict for JSON serialization
            response_data = {
                "tool_code": generated_tool.tool_code,
                "tool_config": generated_tool.tool_config,
                "dependencies": generated_tool.dependencies,
                "validation": {
                    "is_valid": generated_tool.validation.is_valid,
                    "errors": generated_tool.validation.errors,
                    "warnings": generated_tool.validation.warnings,
                    "suggestions": generated_tool.validation.suggestions
                } if generated_tool.validation else None,
                "documentation": generated_tool.documentation,
                "deployment_instructions": generated_tool.deployment_instructions,
                "generated_at": datetime.now().isoformat(),
                "platform": "crewai"
            }

            # Write JSON to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            self.logger.info(
                "Complete response saved to JSON",
                tool_name=tool_name,
                filepath=filepath,
                file_size=len(json.dumps(response_data))
            )

        except Exception as e:
            self.logger.warning(
                "Failed to save response to JSON",
                tool_name=tool_name,
                error=str(e)
            )

    def _generate_test_file(self, spec: ToolSpec, tool_code: str):
        """
        Generate and save test file for the generated tool

        Args:
            spec: The ToolSpec used to generate the tool
            tool_code: The generated tool code
        """
        try:
            # Generate test content
            test_content = self.test_generator.generate_test_file(spec, tool_code)

            # Create tests directory
            output_dir = os.path.join("/app/data", "generated_tools", "tests")
            os.makedirs(output_dir, exist_ok=True)

            # Create __init__.py in tests directory if it doesn't exist
            init_file = os.path.join(output_dir, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""Auto-generated tests for CrewAI tools"""\n')

            # Save test file with test_ prefix
            snake_case_name = self._to_snake_case(spec.name)
            test_filename = f"test_{snake_case_name}.py"
            test_filepath = os.path.join(output_dir, test_filename)

            with open(test_filepath, 'w', encoding='utf-8') as f:
                f.write(test_content)

            self.logger.info(
                "Test file generated successfully",
                tool_name=spec.name,
                test_file=test_filename,
                filepath=test_filepath,
                file_size=len(test_content)
            )

        except Exception as e:
            self.logger.warning(
                "Failed to generate test file",
                tool_name=spec.name,
                error=str(e)
            )

    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
