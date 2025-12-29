"""
Documentation and Usage Examples Generator for CrewAI Tools

Automatically generates comprehensive documentation including:
- Usage examples with realistic scenarios
- Quick-start guides
- API reference documentation
- Integration examples
- Best practices

Phase: 2.2 - Usage Examples & Documentation
Author: Component Factory
Date: 2025-12-21
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import structlog
from base_classes import ToolSpec, ToolInputParameter


logger = structlog.get_logger().bind(component="documentation_generator")


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class UsageExample:
    """
    Represents a usage example for a tool

    Attributes:
        title: Example title (e.g., "Basic Usage", "Advanced Configuration")
        description: What this example demonstrates
        code: Python code for the example
        output: Expected output (optional)
        notes: Additional notes or explanations
    """
    title: str
    description: str
    code: str
    output: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Documentation:
    """
    Complete documentation for a tool

    Attributes:
        tool_name: Name of the tool
        overview: Brief overview of the tool
        version_compatibility: Version compatibility information
        installation: Installation instructions
        quick_start: Quick start guide
        usage_examples: List of usage examples
        api_reference: API documentation
        parameters_doc: Parameter documentation
        best_practices: Best practices list
        crewai_studio_guide: CrewAI Studio complete setup guide with LLM configuration
        troubleshooting: Common issues and solutions
    """
    tool_name: str
    overview: str
    version_compatibility: str
    installation: str
    quick_start: str
    usage_examples: List[UsageExample]
    api_reference: str
    parameters_doc: str
    best_practices: List[str]
    crewai_studio_guide: str
    troubleshooting: List[Dict[str, str]]


# ============================================================================
# DOCUMENTATION GENERATOR
# ============================================================================

class DocumentationGenerator:
    """
    Generates comprehensive documentation and usage examples for CrewAI tools

    Features:
    - Automatic usage example generation
    - Quick-start guides
    - Parameter documentation
    - Integration examples
    - Best practices
    """

    def __init__(self):
        """Initialize the documentation generator"""
        self.logger = logger.bind(component="documentation_generator")

    def generate(self, spec: ToolSpec, tool_code: str) -> Documentation:
        """
        Generate complete documentation for a tool

        Args:
            spec: ToolSpec object with tool specification
            tool_code: Generated tool code

        Returns:
            Documentation object with all documentation sections
        """
        self.logger.info("Generating documentation", tool_name=spec.name)

        # Generate all documentation sections
        overview = self._generate_overview(spec)
        version_compatibility = self._generate_version_compatibility()
        installation = self._generate_installation(spec)
        quick_start = self._generate_quick_start(spec)
        usage_examples = self._generate_usage_examples(spec)
        api_reference = self._generate_api_reference(spec)
        parameters_doc = self._generate_parameters_documentation(spec)
        best_practices = self._generate_best_practices(spec)
        crewai_studio_guide = self._generate_crewai_studio_guide(spec)
        troubleshooting = self._generate_troubleshooting(spec)

        doc = Documentation(
            tool_name=spec.name,
            overview=overview,
            version_compatibility=version_compatibility,
            installation=installation,
            quick_start=quick_start,
            usage_examples=usage_examples,
            api_reference=api_reference,
            parameters_doc=parameters_doc,
            best_practices=best_practices,
            crewai_studio_guide=crewai_studio_guide,
            troubleshooting=troubleshooting
        )

        self.logger.info("Documentation generated",
            tool_name=spec.name,
            examples_count=len(usage_examples),
            best_practices_count=len(best_practices)
        )

        return doc

    def _generate_overview(self, spec: ToolSpec) -> str:
        """Generate tool overview section"""
        lines = []
        lines.append(f"# {spec.display_name}")
        lines.append("")
        lines.append(f"**Category:** {spec.category}")
        lines.append(f"**Version:** {spec.version}")
        lines.append(f"**Author:** {spec.author}")
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        lines.append(spec.description)
        lines.append("")

        if spec.requirements:
            lines.append("**Key Features:**")
            for req in spec.requirements:
                lines.append(f"- {req}")
            lines.append("")

        return "\n".join(lines)

    def _generate_version_compatibility(self) -> str:
        """Generate version compatibility section"""
        lines = []
        lines.append("## Version Compatibility")
        lines.append("")
        lines.append("This tool was generated to work with the following versions:")
        lines.append("")
        lines.append("**CrewAI Compatibility:**")
        lines.append("- **Recommended:** CrewAI 1.5.0+")
        lines.append("- **Minimum:** CrewAI 0.80.0+")
        lines.append("- **Tested with:** CrewAI 1.5.0")
        lines.append("")
        lines.append("**CrewAI Studio:**")
        lines.append("- **Compatible with:** CrewAI Studio (Latest version from [GitHub](https://github.com/strnad/CrewAI-Studio))")
        lines.append("- **Note:** This tool includes a fix for CrewAI Studio's `tasks_output` attribute error in `pg_crew_run.py`")
        lines.append("")
        lines.append("**Python Version:**")
        lines.append("- **Minimum:** Python 3.10+")
        lines.append("- **Recommended:** Python 3.11 or 3.12")
        lines.append("")
        lines.append("**Important Notes:**")
        lines.append("- The code generator targets CrewAI 1.5.0 features and APIs")
        lines.append("- Tools generated include proper error handling for JSON serialization (handles `\"None\"` and `\"null\"` strings from CrewAI Studio)")
        lines.append("- If you encounter `AttributeError: 'str' object has no attribute 'tasks_output'`, ensure you're using the latest CrewAI Studio with the pg_crew_run.py fix")
        lines.append("")
        return "\n".join(lines)

    def _generate_installation(self, spec: ToolSpec) -> str:
        """Generate installation instructions"""
        lines = []
        lines.append("## Installation")
        lines.append("")

        if spec.dependencies:
            lines.append("### Requirements")
            lines.append("")
            lines.append("Install required dependencies:")
            lines.append("")
            lines.append("```bash")
            lines.append(f"pip install {' '.join(spec.dependencies)}")
            lines.append("```")
            lines.append("")

        lines.append("### Installing the Tool")
        lines.append("")
        lines.append("```bash")
        lines.append("# Copy the tool file to your CrewAI project")
        snake_name = self._to_snake_case(spec.name)
        lines.append(f"cp {snake_name}.py /path/to/your/crewai/project/tools/")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def _generate_quick_start(self, spec: ToolSpec) -> str:
        """Generate quick start guide"""
        lines = []
        lines.append("## Quick Start")
        lines.append("")
        lines.append("### 1. Import the Tool")
        lines.append("")
        lines.append("```python")
        snake_name = self._to_snake_case(spec.name)
        lines.append(f"from tools.{snake_name} import {spec.name}")
        lines.append("```")
        lines.append("")

        # Get config and runtime params
        config_params = spec.get_normalized_config_params()
        runtime_params = spec.get_normalized_inputs()

        lines.append("### 2. Initialize the Tool")
        lines.append("")
        lines.append("```python")
        if config_params:
            # Generate initialization with config params
            params = []
            for param in config_params:
                value = self._get_example_value(param)
                params.append(f"{param.name}={value}")
            lines.append(f"tool = {spec.name}({', '.join(params)})")
        else:
            lines.append(f"tool = {spec.name}()")
        lines.append("```")
        lines.append("")

        lines.append("### 3. Use the Tool")
        lines.append("")
        lines.append("```python")
        if runtime_params:
            # Generate usage with runtime params
            params = []
            for param in runtime_params:
                if param.required:
                    value = self._get_example_value(param)
                    params.append(f"{param.name}={value}")

            lines.append(f"result = tool._run({', '.join(params)})")
        else:
            lines.append("result = tool._run()")
        lines.append("print(result)")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def _generate_usage_examples(self, spec: ToolSpec) -> List[UsageExample]:
        """Generate comprehensive usage examples"""
        examples = []

        # Example 1: Basic Usage
        examples.append(self._create_basic_example(spec))

        # Example 2: With Optional Parameters (if any)
        runtime_params = spec.get_normalized_inputs()
        optional_params = [p for p in runtime_params if not p.required]
        if optional_params:
            examples.append(self._create_optional_params_example(spec, optional_params))

        # Example 3: Integration with CrewAI Agent
        examples.append(self._create_crewai_integration_example(spec))

        # Example 4: Error Handling
        examples.append(self._create_error_handling_example(spec))

        return examples

    def _create_basic_example(self, spec: ToolSpec) -> UsageExample:
        """Create basic usage example"""
        runtime_params = spec.get_normalized_inputs()
        config_params = spec.get_normalized_config_params()

        code_lines = []
        code_lines.append(f"from tools.{self._to_snake_case(spec.name)} import {spec.name}")
        code_lines.append("")
        code_lines.append("# Initialize the tool")

        if config_params:
            init_params = [f"{p.name}={self._get_example_value(p)}" for p in config_params[:2]]
            code_lines.append(f"tool = {spec.name}({', '.join(init_params)})")
        else:
            code_lines.append(f"tool = {spec.name}()")

        code_lines.append("")
        code_lines.append("# Execute the tool")

        if runtime_params:
            exec_params = [f"{p.name}={self._get_example_value(p)}" for p in runtime_params if p.required]
            code_lines.append(f"result = tool._run({', '.join(exec_params)})")
        else:
            code_lines.append("result = tool._run()")

        code_lines.append("")
        code_lines.append("# Process results")
        code_lines.append("print(f\"Result: {result}\")")

        return UsageExample(
            title="Basic Usage",
            description=f"Simple example showing how to use {spec.display_name}",
            code="\n".join(code_lines),
            output="Result: <tool output>",
            notes="This is the most basic usage pattern. Customize parameters based on your needs."
        )

    def _create_optional_params_example(self, spec: ToolSpec, optional_params: List[ToolInputParameter]) -> UsageExample:
        """Create example with optional parameters"""
        runtime_params = spec.get_normalized_inputs()

        code_lines = []
        code_lines.append(f"from tools.{self._to_snake_case(spec.name)} import {spec.name}")
        code_lines.append("")
        code_lines.append(f"tool = {spec.name}()")
        code_lines.append("")
        code_lines.append("# Using optional parameters for more control")

        all_params = []
        for param in runtime_params:
            value = self._get_example_value(param)
            all_params.append(f"{param.name}={value}")

        code_lines.append(f"result = tool._run(")
        for i, param_str in enumerate(all_params):
            if i < len(all_params) - 1:
                code_lines.append(f"    {param_str},")
            else:
                code_lines.append(f"    {param_str}")
        code_lines.append(")")
        code_lines.append("")
        code_lines.append("print(result)")

        return UsageExample(
            title="Using Optional Parameters",
            description=f"Example showing how to use optional parameters for fine-tuned control",
            code="\n".join(code_lines),
            notes="Optional parameters allow you to customize the tool's behavior. See API Reference for all available parameters."
        )

    def _create_crewai_integration_example(self, spec: ToolSpec) -> UsageExample:
        """Create CrewAI integration example"""
        runtime_params = spec.get_normalized_inputs()

        code_lines = []
        code_lines.append("from crewai import Agent, Task, Crew")
        code_lines.append(f"from tools.{self._to_snake_case(spec.name)} import {spec.name}")
        code_lines.append("")
        code_lines.append("# Create an agent with the tool")
        code_lines.append("agent = Agent(")
        code_lines.append(f'    role="{spec.category.title()} Specialist",')
        code_lines.append(f'    goal="Perform {spec.category} operations efficiently",')
        code_lines.append(f'    backstory="Expert in {spec.category} with advanced capabilities",')
        code_lines.append(f"    tools=[{spec.name}()],")
        code_lines.append("    verbose=True")
        code_lines.append(")")
        code_lines.append("")
        code_lines.append("# Create a task")
        code_lines.append("task = Task(")

        # Generate task description based on first required parameter
        if runtime_params:
            first_param = next((p for p in runtime_params if p.required), runtime_params[0])
            code_lines.append(f'    description="Use the {spec.display_name} to process {first_param.description.lower()}",')
        else:
            code_lines.append(f'    description="Use the {spec.display_name} to complete the task",')

        code_lines.append(f'    expected_output="Processed results from {spec.display_name}",')
        code_lines.append("    agent=agent")
        code_lines.append(")")
        code_lines.append("")
        code_lines.append("# Create and run crew")
        code_lines.append("crew = Crew(agents=[agent], tasks=[task])")
        code_lines.append("result = crew.kickoff()")
        code_lines.append("print(result)")

        return UsageExample(
            title="Integration with CrewAI",
            description=f"Example showing how to integrate {spec.display_name} with a CrewAI agent",
            code="\n".join(code_lines),
            notes="This example shows how to use the tool within a CrewAI workflow. The agent will automatically use the tool when needed."
        )

    def _create_error_handling_example(self, spec: ToolSpec) -> UsageExample:
        """Create error handling example"""
        runtime_params = spec.get_normalized_inputs()

        code_lines = []
        code_lines.append(f"from tools.{self._to_snake_case(spec.name)} import {spec.name}")
        code_lines.append("")
        code_lines.append(f"tool = {spec.name}()")
        code_lines.append("")
        code_lines.append("# Wrap tool execution in error handling")
        code_lines.append("try:")

        if runtime_params:
            exec_params = [f"{p.name}={self._get_example_value(p)}" for p in runtime_params if p.required]
            code_lines.append(f"    result = tool._run({', '.join(exec_params)})")
        else:
            code_lines.append("    result = tool._run()")

        code_lines.append("    ")
        code_lines.append("    # Check if result contains errors")
        code_lines.append('    if isinstance(result, dict) and "error" in result:')
        code_lines.append('        print(f"Tool error: {result[\'error\']}")')
        code_lines.append("    else:")
        code_lines.append('        print(f"Success: {result}")')
        code_lines.append("        ")
        code_lines.append("except Exception as e:")
        code_lines.append('    print(f"Unexpected error: {str(e)}")')

        return UsageExample(
            title="Error Handling",
            description="Example showing proper error handling when using the tool",
            code="\n".join(code_lines),
            notes="Always wrap tool execution in try-except blocks to handle potential errors gracefully."
        )

    def _generate_api_reference(self, spec: ToolSpec) -> str:
        """Generate API reference documentation"""
        lines = []
        lines.append("## API Reference")
        lines.append("")
        lines.append(f"### `{spec.name}`")
        lines.append("")
        lines.append(f"**Description:** {spec.description}")
        lines.append("")

        # Constructor
        config_params = spec.get_normalized_config_params()
        if config_params:
            lines.append("#### Constructor")
            lines.append("")
            lines.append("```python")
            param_strs = [f"{p.name}: {p.type}" for p in config_params]
            lines.append(f"__init__(self, {', '.join(param_strs)})")
            lines.append("```")
            lines.append("")

        # _run method
        runtime_params = spec.get_normalized_inputs()
        lines.append("#### `_run()` Method")
        lines.append("")
        lines.append("```python")
        if runtime_params:
            param_strs = [f"{p.name}: {p.type}" for p in runtime_params]
            lines.append(f"_run(self, {', '.join(param_strs)}) -> Any")
        else:
            lines.append("_run(self) -> Any")
        lines.append("```")
        lines.append("")
        lines.append(f"**Description:** {spec.description}")
        lines.append("")

        return "\n".join(lines)

    def _generate_parameters_documentation(self, spec: ToolSpec) -> str:
        """Generate detailed parameters documentation"""
        lines = []
        lines.append("## Parameters")
        lines.append("")

        # Configuration Parameters
        config_params = spec.get_normalized_config_params()
        if config_params:
            lines.append("### Configuration Parameters")
            lines.append("")
            lines.append("Parameters passed to the constructor (`__init__`):")
            lines.append("")

            for param in config_params:
                lines.append(f"#### `{param.name}`")
                lines.append("")
                lines.append(f"- **Type:** `{param.type}`")
                lines.append(f"- **Required:** {'Yes' if param.required else 'No'}")
                if param.default_value is not None:
                    lines.append(f"- **Default:** `{param.default_value}`")
                lines.append(f"- **Description:** {param.description}")

                if param.examples:
                    lines.append(f"- **Examples:**")
                    for example in param.examples:
                        lines.append(f"  - `{example}`")

                lines.append("")

        # Runtime Parameters
        runtime_params = spec.get_normalized_inputs()
        if runtime_params:
            lines.append("### Runtime Parameters")
            lines.append("")
            lines.append("Parameters passed to the `_run()` method:")
            lines.append("")

            for param in runtime_params:
                lines.append(f"#### `{param.name}`")
                lines.append("")
                lines.append(f"- **Type:** `{param.type}`")
                lines.append(f"- **Required:** {'Yes' if param.required else 'No'}")
                if param.default_value is not None:
                    lines.append(f"- **Default:** `{param.default_value}`")
                lines.append(f"- **Description:** {param.description}")

                if param.examples:
                    lines.append(f"- **Examples:**")
                    for example in param.examples:
                        lines.append(f"  - `{example}`")

                lines.append("")

        return "\n".join(lines)

    def _generate_best_practices(self, spec: ToolSpec) -> List[str]:
        """Generate best practices list"""
        practices = []

        # General best practices
        practices.append("Always handle errors gracefully using try-except blocks")
        practices.append("Validate input parameters before passing to the tool")

        # Parameter-specific practices
        runtime_params = spec.get_normalized_inputs()
        if any('timeout' in p.name.lower() for p in runtime_params):
            practices.append("Set appropriate timeout values to prevent hanging operations")

        if any('api' in p.name.lower() or 'key' in p.name.lower() for p in runtime_params):
            practices.append("Store API keys securely using environment variables")
            practices.append("Never hardcode sensitive credentials in your code")

        if any(p.type.startswith('List') for p in runtime_params):
            practices.append("Check list lengths before processing to avoid performance issues")

        # Category-specific practices
        if spec.category == 'api':
            practices.append("Implement retry logic for transient API failures")
            practices.append("Use connection pooling for better performance")
        elif spec.category == 'database':
            practices.append("Use connection pooling to manage database connections efficiently")
            practices.append("Always close database connections when done")
        elif spec.category == 'file':
            practices.append("Use context managers (with statements) for file operations")
            practices.append("Validate file paths and permissions before operations")

        practices.append("Use the tool within CrewAI agents for autonomous task execution")
        practices.append("Monitor tool execution time and optimize as needed")

        return practices

    def _generate_crewai_studio_guide(self, spec: ToolSpec) -> str:
        """Generate comprehensive CrewAI Studio setup guide"""
        tool_name = spec.display_name or spec.name

        # Get first runtime parameter for example
        runtime_params = spec.get_normalized_inputs()
        example_param = runtime_params[0] if runtime_params else None
        example_input = ""
        if example_param and example_param.examples:
            example_input = example_param.examples[0]
        elif example_param:
            example_input = "your_input_here"

        guide = f"""## CrewAI Studio Setup Guide

### Recommended LLM Configuration

**For Local Development (Recommended):**
- **LLM Provider:** Ollama
- **Model:** llama3.2 (default)
- **Alternative Models:** llama3.1, mistral, codellama, or any Ollama-compatible model

**Why Ollama 3.2?**
- Free and runs locally (no API costs)
- Good balance of performance and resource usage
- Works well with tool-calling patterns
- Privacy-friendly (data stays on your machine)

**Other Supported LLMs:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic Claude
- Google Gemini
- Any OpenAI-compatible API

### Step-by-Step Setup for {tool_name}

#### 1. Create Your Crew

In CrewAI Studio:
1. Click "New Crew"
2. Name it: "{tool_name} Crew"
3. Save

#### 2. Configure the Agent

Go to the **Agents** page and create a new agent with these **EXACT** settings:

**Basic Settings:**
- **Role:** {tool_name} Expert
- **Goal:** Use the {tool_name} tool and return only the result
- **Backstory:** You are a specialist that uses the {tool_name} tool and returns direct results

**CRITICAL Agent Settings (These prevent LLM confusion):**

✅ **Max Iterations:** `1`
   - Forces the agent to respond immediately
   - Prevents infinite loops

❌ **Allow Delegation:** UNCHECKED
   - Prevents the agent from trying to delegate to other agents
   - Forces it to use the tool directly

✅ **Temperature:** `0` or `0.1`
   - Makes responses deterministic
   - Reduces hallucinations
   - Ensures consistent tool usage

❌ **Memory:** UNCHECKED (if available)
   - Prevents context pollution
   - Avoids confusion from previous runs

❌ **Verbose:** UNCHECKED
   - Cleaner output
   - Faster execution

#### 3. Add the Tool

1. Go to **Tools** page
2. Click "Add Custom Tool"
3. Paste the {tool_name} code
4. Save the tool
5. Assign it to your "{tool_name} Expert" agent

#### 4. Create the Task

Go to **Tasks** page and create a task:

**Task Settings:**
- **Description:** Use the {tool_name} tool with input "{example_input}" and return the result
- **Expected Output:** The direct result from the tool
- **Agent:** {tool_name} Expert

**Task Description Template:**
```
Use the {tool_name} with [describe inputs] and return only the result.
```

**DON'T use complex instructions like:**
❌ "Calculate X. Use the tool ONCE, then immediately provide the final answer"
❌ "First do X, then Y, then provide output"

**DO use simple, direct instructions:**
✅ "Use the {tool_name} with input 'X' and return the result"

#### 5. Quick Test Configuration

**Agent Checklist:**
- ✅ Max Iterations: 1
- ❌ Allow Delegation: OFF
- ✅ Temperature: 0-0.1
- ❌ Memory: OFF
- ❌ Verbose: OFF

**Task Checklist:**
- ✅ Simple, direct description
- ✅ Clear expected output
- ✅ Assigned to correct agent

#### 6. Configure Crew Settings

Go to **Crew Settings** and configure these **RECOMMENDED** settings:

**Process:**
- Select: **Sequential** (Recommended for beginners)
- Sequential executes tasks in order, one after another
- Hierarchical requires a manager agent (more complex)

**Crew-Level Settings:**

❌ **Verbose:** UNCHECKED
   - Reduces noise in output
   - Shows only essential information
   - Recommended: OFF for cleaner results

❌ **Memory:** UNCHECKED
   - Prevents crew from remembering past executions
   - Avoids context pollution between runs
   - Recommended: OFF for consistent behavior

❌ **Cache:** UNCHECKED
   - Disables result caching
   - Ensures fresh results every time
   - Recommended: OFF for tool testing

❌ **Planning:** UNCHECKED
   - Disables automatic planning mode
   - Not needed for simple tool usage
   - Recommended: OFF for direct execution

**Rate Limiting:**
- **Max RPM (Requests Per Minute):** 10
  - Prevents overwhelming APIs
  - Adjust based on your LLM provider limits
  - Ollama: Can handle higher (20-30)
  - OpenAI free tier: Keep at 3-5
  - OpenAI paid: Can use 60+

**Add Tasks to Crew:**
1. In Crew settings, find "Tasks" section
2. Add the task you created in Step 4
3. Tasks will execute in the order you add them
4. For this simple example, you only need 1 task

**Crew Configuration Summary:**
```yaml
process: sequential
verbose: false
memory: false
cache: false
planning: false
max_rpm: 10
tasks:
  - your_calculator_task
```

#### 7. Run Your Crew

1. Click "Run Crew"
2. Monitor the output
3. The agent should use the tool immediately and return results
4. Verify the result matches your expected output

**What to Expect:**
- Agent receives the task
- Agent calls the {tool_name} tool with your input
- Tool executes and returns result
- Agent returns the result as final output

### Troubleshooting LLM Issues

**Problem:** Agent doesn't use the tool
**Solution:**
- Ensure "Allow Delegation" is UNCHECKED
- Set Max Iterations to 1
- Simplify task description

**Problem:** Agent hallucinates or gives wrong answers
**Solution:**
- Set Temperature to 0
- Disable Memory
- Make task description more specific

**Problem:** Agent loops infinitely
**Solution:**
- Set Max Iterations to 1
- Check that the tool returns a string (not dict/object)

**Problem:** "Tool not found" error
**Solution:**
- Verify tool is assigned to the agent
- Check tool name matches exactly
- Restart CrewAI Studio

### Example Working Configuration

**Agent:**
```yaml
role: Calculator Expert
goal: Return only numerical results using the calculator tool
backstory: You use the Playground Calculator tool and return only numbers
max_iterations: 1
allow_delegation: false
temperature: 0
```

**Task:**
```yaml
description: Use the Playground Calculator with input "2+2*3" and return only the number
expected_output: 8
agent: Calculator Expert
```

**Crew:**
```yaml
process: sequential
verbose: false
memory: false
cache: false
planning: false
max_rpm: 10
tasks:
  - calculator_task
```

**Result:** The agent immediately uses the tool and returns `8`.

### Tips for Success

1. **Start Simple:** Test with basic inputs first
2. **One Tool Per Agent:** Don't overload agents with multiple tools initially
3. **Clear Instructions:** Be explicit about what you want
4. **Monitor Iterations:** If it takes >1 iteration, something's wrong
5. **Temperature Matters:** 0 = deterministic, 1 = creative (use 0 for tools)

---
"""
        return guide

    def _generate_troubleshooting(self, spec: ToolSpec) -> List[Dict[str, str]]:
        """Generate troubleshooting guide"""
        issues = []

        # Common issue 1: Import errors
        issues.append({
            "problem": "ImportError when trying to import the tool",
            "solution": f"Ensure the tool file is in your Python path. Try: `export PYTHONPATH=$PYTHONPATH:/path/to/tools`"
        })

        # Common issue 2: Parameter errors
        runtime_params = spec.get_normalized_inputs()
        required_params = [p for p in runtime_params if p.required]
        if required_params:
            param_names = ', '.join([f'`{p.name}`' for p in required_params[:2]])
            issues.append({
                "problem": "Missing required parameter error",
                "solution": f"Ensure you provide all required parameters: {param_names}. Check the Parameters section for details."
            })

        # Common issue 3: Type errors
        if runtime_params:
            issues.append({
                "problem": "Type validation error",
                "solution": "Verify that parameter types match the expected types. Use the correct Python types (e.g., list for List[str], dict for Dict[str, Any])."
            })

        # Category-specific issues
        if spec.category == 'api':
            issues.append({
                "problem": "Connection timeout or API errors",
                "solution": "Check your internet connection, verify API credentials, and ensure the API endpoint is accessible. Consider increasing timeout values."
            })
        elif spec.category == 'database':
            issues.append({
                "problem": "Database connection failed",
                "solution": "Verify database credentials, check that the database server is running, and ensure network connectivity."
            })
        elif spec.category == 'file':
            issues.append({
                "problem": "File not found or permission denied",
                "solution": "Check that the file path is correct and that your application has the necessary read/write permissions."
            })

        # Dependencies issue
        if spec.dependencies:
            issues.append({
                "problem": "Module not found error",
                "solution": f"Install required dependencies: `pip install {' '.join(spec.dependencies)}`"
            })

        return issues

    def _get_example_value(self, param: ToolInputParameter) -> str:
        """Generate example value for a parameter"""
        # Use default value if available
        if param.default_value is not None:
            if isinstance(param.default_value, str):
                return f'"{param.default_value}"'
            return str(param.default_value)

        # Use examples if available
        if param.examples and len(param.examples) > 0:
            return param.examples[0]

        # Generate based on type
        type_lower = param.type.lower()

        if 'api_key' in param.name.lower() or 'token' in param.name.lower():
            return '"your_api_key_here"'
        elif 'url' in param.name.lower() or 'endpoint' in param.name.lower():
            return '"https://api.example.com"'
        elif 'path' in param.name.lower() or 'file' in param.name.lower():
            return '"/path/to/file.txt"'
        elif param.type == 'str':
            return f'"example_{param.name}"'
        elif param.type == 'int':
            return '10'
        elif param.type == 'float':
            return '10.5'
        elif param.type == 'bool':
            return 'True'
        elif 'list[str]' in type_lower:
            return '["item1", "item2", "item3"]'
        elif 'list[int]' in type_lower:
            return '[1, 2, 3]'
        elif 'dict' in type_lower:
            return '{"key": "value"}'
        elif 'optional' in type_lower:
            return 'None'
        else:
            return f'"example_{param.name}"'

    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def to_markdown(self, doc: Documentation) -> str:
        """
        Convert Documentation object to complete Markdown file

        Args:
            doc: Documentation object

        Returns:
            Markdown formatted documentation string
        """
        lines = []

        # Title and overview
        lines.append(doc.overview)

        # Version compatibility
        lines.append(doc.version_compatibility)

        # Installation
        lines.append(doc.installation)

        # Quick Start
        lines.append(doc.quick_start)

        # Usage Examples
        lines.append("## Usage Examples")
        lines.append("")

        for i, example in enumerate(doc.usage_examples, 1):
            lines.append(f"### Example {i}: {example.title}")
            lines.append("")
            lines.append(example.description)
            lines.append("")
            lines.append("```python")
            lines.append(example.code)
            lines.append("```")
            lines.append("")

            if example.output:
                lines.append("**Expected Output:**")
                lines.append("```")
                lines.append(example.output)
                lines.append("```")
                lines.append("")

            if example.notes:
                lines.append(f"**Note:** {example.notes}")
                lines.append("")

        # API Reference
        lines.append(doc.api_reference)

        # Parameters
        lines.append(doc.parameters_doc)

        # Best Practices
        lines.append("## Best Practices")
        lines.append("")
        for practice in doc.best_practices:
            lines.append(f"- {practice}")
        lines.append("")

        # CrewAI Studio Guide
        lines.append(doc.crewai_studio_guide)

        # Troubleshooting
        lines.append("## Troubleshooting")
        lines.append("")
        for issue in doc.troubleshooting:
            lines.append(f"### {issue['problem']}")
            lines.append("")
            lines.append(f"**Solution:** {issue['solution']}")
            lines.append("")

        return "\n".join(lines)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_documentation(spec: ToolSpec, tool_code: str) -> Documentation:
    """
    Quick documentation generation function

    Args:
        spec: ToolSpec object
        tool_code: Generated tool code

    Returns:
        Documentation object
    """
    generator = DocumentationGenerator()
    return generator.generate(spec, tool_code)


def save_documentation(doc: Documentation, output_path: str) -> None:
    """
    Save documentation to a Markdown file

    Args:
        doc: Documentation object
        output_path: Path to save the documentation file
    """
    generator = DocumentationGenerator()
    markdown = generator.to_markdown(doc)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    from base_classes import ToolSpec, ToolInputParameter

    # Example usage
    spec = ToolSpec(
        name="WebScraperTool",
        display_name="Web Scraper",
        description="Scrape and extract data from web pages",
        category="web",
        requirements=[
            "Extract text content from web pages",
            "Support CSS selectors",
            "Handle dynamic content"
        ],
        inputs=[
            ToolInputParameter(
                name="url",
                type="str",
                description="URL of the web page to scrape",
                required=True
            ),
            ToolInputParameter(
                name="selector",
                type="str",
                description="CSS selector for elements to extract",
                required=False,
                default_value="body"
            )
        ],
        config_params=[
            ToolInputParameter(
                name="timeout",
                type="int",
                description="Request timeout in seconds",
                required=False,
                default_value=30,
                param_kind="config"
            )
        ],
        dependencies=["requests", "beautifulsoup4"],
        author="Component Factory",
        version="1.0.0"
    )

    # Generate documentation
    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Convert to markdown
    markdown = generator.to_markdown(doc)
    print(markdown)
