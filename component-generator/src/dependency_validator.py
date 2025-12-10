"""
Dependency validator for crewAI tool generation

This module validates dependencies against CrewAI-Studio supported libraries
and provides detailed feedback, warnings, and manual implementation suggestions.

Author: CrewAI Tool Generator Team
Created: 2025-12-11
Phase: 1.2 - Dependency Validation
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
import structlog

from supported_libraries import (
    is_supported,
    is_stdlib,
    validate_dependencies,
    get_alternatives,
    get_category,
    STDLIB_MODULES,
    SUPPORTED_LIBRARIES,
)


logger = structlog.get_logger().bind(component="dependency_validator")


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class DependencyValidationResult:
    """
    Result of dependency validation

    Attributes:
        all_supported: True if all dependencies are supported
        supported: List of supported dependencies
        unsupported: List of unsupported dependencies
        stdlib: List of stdlib dependencies
        external: List of external library dependencies
        alternatives: Dictionary mapping unsupported deps to alternatives
        manual_implementation_needed: True if manual implementation is needed
        warnings: List of warning messages
        suggestions: List of suggestion messages
        can_proceed: True if tool generation can proceed
        severity: Severity level (success, warning, error)
    """
    all_supported: bool
    supported: List[str]
    unsupported: List[str]
    stdlib: List[str]
    external: List[str]
    alternatives: Dict[str, List[str]]
    manual_implementation_needed: bool
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    can_proceed: bool = True
    severity: str = "success"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "all_supported": self.all_supported,
            "supported": self.supported,
            "unsupported": self.unsupported,
            "stdlib": self.stdlib,
            "external": self.external,
            "alternatives": self.alternatives,
            "manual_implementation_needed": self.manual_implementation_needed,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "can_proceed": self.can_proceed,
            "severity": self.severity,
            "summary": {
                "total": len(self.supported) + len(self.unsupported),
                "supported_count": len(self.supported),
                "unsupported_count": len(self.unsupported),
                "stdlib_count": len(self.stdlib),
                "external_count": len(self.external),
            }
        }


# ============================================================================
# DEPENDENCY VALIDATOR CLASS
# ============================================================================

class DependencyValidator:
    """
    Validates tool dependencies against CrewAI-Studio environment

    This validator ensures that generated tools only use libraries available
    in the CrewAI-Studio environment, or provides manual implementation
    suggestions when dependencies are not available.

    Features:
    - Validates against 253 supported libraries
    - Detects Python stdlib modules (always available)
    - Suggests alternatives for unsupported libraries
    - Recommends manual implementations
    - Provides detailed warnings and suggestions

    Example:
        >>> validator = DependencyValidator()
        >>> result = validator.validate(["requests", "pandas", "unsupported_lib"])
        >>> print(result.warnings)
        ['unsupported_lib is not available in CrewAI-Studio']
        >>> print(result.alternatives)
        {'unsupported_lib': ['Implement manually using Python stdlib']}
    """

    def __init__(self):
        """Initialize the dependency validator"""
        self.logger = structlog.get_logger().bind(component="dependency_validator")
        self._load_validation_rules()

    def _load_validation_rules(self):
        """Load validation rules and patterns"""
        # Common patterns for manual implementation
        self.manual_implementation_patterns = {
            "http_client": {
                "triggers": ["requests", "httpx", "urllib3"],
                "manual_libs": ["urllib.request", "http.client", "socket"],
                "description": "HTTP client functionality"
            },
            "json_processing": {
                "triggers": ["ujson", "simplejson", "orjson"],
                "manual_libs": ["json"],
                "description": "JSON parsing and serialization"
            },
            "csv_processing": {
                "triggers": ["csv"],
                "manual_libs": ["csv"],
                "description": "CSV file processing"
            },
            "file_operations": {
                "triggers": ["pathlib", "os"],
                "manual_libs": ["pathlib", "os", "shutil"],
                "description": "File and directory operations"
            },
            "date_time": {
                "triggers": ["arrow", "pendulum", "dateutil"],
                "manual_libs": ["datetime", "time", "calendar"],
                "description": "Date and time operations"
            },
            "text_processing": {
                "triggers": ["re", "string"],
                "manual_libs": ["re", "string", "textwrap"],
                "description": "Text and regex operations"
            },
            "data_structures": {
                "triggers": ["collections", "dataclasses"],
                "manual_libs": ["collections", "dataclasses", "typing"],
                "description": "Advanced data structures"
            },
        }

        # Libraries that require special attention
        self.special_attention_libs = {
            "crewai": "Core CrewAI library - ensure proper usage of BaseTool",
            "crewai-tools": "Official CrewAI tools - check for existing implementations",
            "anthropic": "Anthropic API - requires API key configuration",
            "openai": "OpenAI API - requires API key configuration",
            "chromadb": "Vector database - ensure proper initialization",
            "pandas": "Data processing - can be heavy, consider stdlib alternatives",
            "numpy": "Numeric processing - can be heavy, consider math/statistics",
        }

    def validate(
        self,
        dependencies: List[str],
        strict: bool = False,
        suggest_manual: bool = True
    ) -> DependencyValidationResult:
        """
        Validate dependencies against CrewAI-Studio environment

        Args:
            dependencies: List of dependency names to validate
            strict: If True, fail on any unsupported dependency
            suggest_manual: If True, suggest manual implementations

        Returns:
            DependencyValidationResult with detailed validation info
        """
        self.logger.info(
            "Starting dependency validation",
            dependency_count=len(dependencies),
            strict_mode=strict
        )

        # Use existing validation function
        base_result = validate_dependencies(dependencies)

        # Build warnings and suggestions
        warnings = []
        suggestions = []
        manual_implementation_needed = False
        can_proceed = True
        severity = "success"

        # Check for unsupported dependencies
        if base_result['unsupported']:
            manual_implementation_needed = True
            severity = "warning" if not strict else "error"

            for dep in base_result['unsupported']:
                warning = f"⚠️  '{dep}' is not available in CrewAI-Studio environment"
                warnings.append(warning)

                # Add alternatives
                alts = base_result['alternatives'].get(dep, [])
                if alts:
                    suggestion = f"💡 Consider using: {', '.join(alts)}"
                    suggestions.append(suggestion)

                # Suggest manual implementation
                if suggest_manual:
                    manual_suggestion = (
                        f"🔧 Manual implementation recommended for '{dep}' "
                        "using Python stdlib"
                    )
                    suggestions.append(manual_suggestion)

            if strict:
                can_proceed = False
                warnings.append(
                    "❌ Strict mode: Cannot proceed with unsupported dependencies"
                )

        # Check for special attention libraries
        for dep in base_result['supported']:
            if dep in self.special_attention_libs:
                note = self.special_attention_libs[dep]
                suggestions.append(f"📝 {dep}: {note}")

        # Add stdlib optimization suggestions
        if base_result['external']:
            stdlib_optimizations = self._suggest_stdlib_alternatives(
                base_result['external']
            )
            if stdlib_optimizations:
                suggestions.extend(stdlib_optimizations)

        # Log validation results
        self._log_validation_result(base_result, warnings, suggestions)

        # Build result object
        result = DependencyValidationResult(
            all_supported=base_result['all_supported'],
            supported=base_result['supported'],
            unsupported=base_result['unsupported'],
            stdlib=base_result['stdlib'],
            external=base_result['external'],
            alternatives=base_result['alternatives'],
            manual_implementation_needed=manual_implementation_needed,
            warnings=warnings,
            suggestions=suggestions,
            can_proceed=can_proceed,
            severity=severity
        )

        return result

    def _suggest_stdlib_alternatives(self, external_deps: List[str]) -> List[str]:
        """
        Suggest stdlib alternatives for external dependencies

        Args:
            external_deps: List of external dependencies

        Returns:
            List of suggestion messages
        """
        suggestions = []

        # Check for common cases where stdlib can replace external lib
        stdlib_replacements = {
            "requests": "urllib.request",
            "httpx": "urllib.request",
            "beautifulsoup4": "html.parser",
            "ujson": "json",
            "simplejson": "json",
            "arrow": "datetime",
            "pendulum": "datetime",
            "python-dateutil": "datetime (for basic operations)",
        }

        for dep in external_deps:
            if dep in stdlib_replacements:
                stdlib_alt = stdlib_replacements[dep]
                suggestion = (
                    f"⚡ Performance tip: '{dep}' could be replaced with "
                    f"stdlib '{stdlib_alt}' for simpler use cases"
                )
                suggestions.append(suggestion)

        return suggestions

    def _log_validation_result(
        self,
        base_result: Dict,
        warnings: List[str],
        suggestions: List[str]
    ):
        """Log detailed validation results"""
        self.logger.info(
            "Dependency validation completed",
            total=base_result['total'],
            supported=base_result['supported_count'],
            unsupported=base_result['unsupported_count'],
            stdlib=len(base_result['stdlib']),
            external=len(base_result['external']),
            all_supported=base_result['all_supported']
        )

        if warnings:
            for warning in warnings:
                self.logger.warning("Validation warning", message=warning)

        if suggestions:
            for suggestion in suggestions:
                self.logger.info("Validation suggestion", message=suggestion)

    def get_manual_implementation_guide(
        self,
        unsupported_dep: str
    ) -> Dict[str, any]:
        """
        Get manual implementation guide for unsupported dependency

        Args:
            unsupported_dep: Name of unsupported dependency

        Returns:
            Dictionary with implementation guide
        """
        # Check if dependency matches any pattern
        for pattern_name, pattern_info in self.manual_implementation_patterns.items():
            if unsupported_dep.lower() in [t.lower() for t in pattern_info['triggers']]:
                return {
                    "dependency": unsupported_dep,
                    "pattern": pattern_name,
                    "description": pattern_info['description'],
                    "recommended_stdlib": pattern_info['manual_libs'],
                    "implementation_approach": self._get_implementation_approach(
                        pattern_name
                    )
                }

        # Default guide
        return {
            "dependency": unsupported_dep,
            "pattern": "custom",
            "description": "Custom implementation needed",
            "recommended_stdlib": ["typing", "dataclasses", "json"],
            "implementation_approach": (
                "Implement core functionality using Python standard library. "
                "Focus on minimal dependencies and clear interfaces."
            )
        }

    def _get_implementation_approach(self, pattern_name: str) -> str:
        """Get implementation approach for a specific pattern"""
        approaches = {
            "http_client": (
                "Use urllib.request for HTTP requests. Example: "
                "urllib.request.urlopen() for GET, Request() for POST. "
                "Handle errors with try/except blocks."
            ),
            "json_processing": (
                "Use built-in json module: json.loads() for parsing, "
                "json.dumps() for serialization. Handles all standard JSON types."
            ),
            "csv_processing": (
                "Use csv module: csv.reader() for reading, csv.writer() for writing. "
                "Use csv.DictReader/DictWriter for dictionary-based operations."
            ),
            "file_operations": (
                "Use pathlib.Path for modern file handling or os/os.path for "
                "legacy code. Use shutil for high-level operations like copy/move."
            ),
            "date_time": (
                "Use datetime module: datetime.now() for current time, "
                "strftime/strptime for formatting. Use timedelta for calculations."
            ),
            "text_processing": (
                "Use re module for regex: re.search(), re.match(), re.findall(). "
                "Use string methods for simple operations."
            ),
            "data_structures": (
                "Use collections: namedtuple, defaultdict, Counter. "
                "Use dataclasses for structured data with type hints."
            ),
        }

        return approaches.get(pattern_name, "Implement using appropriate stdlib modules")

    def validate_imports_in_code(self, code: str) -> DependencyValidationResult:
        """
        Extract and validate imports from generated code

        Args:
            code: Generated Python code

        Returns:
            DependencyValidationResult
        """
        import ast

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.logger.error("Failed to parse code for import validation", error=str(e))
            return DependencyValidationResult(
                all_supported=False,
                supported=[],
                unsupported=[],
                stdlib=[],
                external=[],
                alternatives={},
                manual_implementation_needed=False,
                warnings=[f"⚠️  Syntax error in code: {str(e)}"],
                suggestions=[],
                can_proceed=False,
                severity="error"
            )

        # Extract imports
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

        # Validate extracted imports
        return self.validate(list(imports))

    def generate_requirements_txt(
        self,
        dependencies: List[str]
    ) -> str:
        """
        Generate requirements.txt content for supported dependencies

        Args:
            dependencies: List of dependencies

        Returns:
            requirements.txt formatted string
        """
        result = self.validate(dependencies)

        lines = []
        lines.append("# Generated requirements.txt for crewAI tool")
        lines.append("# Only supported dependencies are included")
        lines.append("")

        # Add supported external dependencies with versions
        for dep in result.external:
            if dep in SUPPORTED_LIBRARIES:
                version = SUPPORTED_LIBRARIES[dep]
                if version and version != "Derived":
                    lines.append(f"{dep}=={version}")
                else:
                    lines.append(dep)

        # Add note about unsupported dependencies
        if result.unsupported:
            lines.append("")
            lines.append("# Unsupported dependencies (manual implementation needed):")
            for dep in result.unsupported:
                lines.append(f"# - {dep}")
                alts = result.alternatives.get(dep, [])
                if alts:
                    lines.append(f"#   Alternatives: {', '.join(alts)}")

        return "\n".join(lines)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def quick_validate(dependencies: List[str]) -> bool:
    """
    Quick validation check - returns True if all dependencies supported

    Args:
        dependencies: List of dependency names

    Returns:
        True if all dependencies are supported
    """
    validator = DependencyValidator()
    result = validator.validate(dependencies)
    return result.all_supported


def get_validation_summary(result: DependencyValidationResult) -> str:
    """
    Get human-readable validation summary

    Args:
        result: DependencyValidationResult

    Returns:
        Formatted summary string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("DEPENDENCY VALIDATION SUMMARY")
    lines.append("=" * 60)

    total = len(result.supported) + len(result.unsupported)
    lines.append(f"Total dependencies: {total}")
    lines.append(f"✅ Supported: {len(result.supported)}")
    lines.append(f"   - Stdlib: {len(result.stdlib)}")
    lines.append(f"   - External: {len(result.external)}")
    lines.append(f"❌ Unsupported: {len(result.unsupported)}")
    lines.append("")

    if result.warnings:
        lines.append("WARNINGS:")
        for warning in result.warnings:
            lines.append(f"  {warning}")
        lines.append("")

    if result.suggestions:
        lines.append("SUGGESTIONS:")
        for suggestion in result.suggestions:
            lines.append(f"  {suggestion}")
        lines.append("")

    lines.append(f"Status: {result.severity.upper()}")
    lines.append(f"Can proceed: {'Yes' if result.can_proceed else 'No'}")

    if result.manual_implementation_needed:
        lines.append("⚠️  Manual implementation required for unsupported dependencies")

    lines.append("=" * 60)

    return "\n".join(lines)


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage and testing
    validator = DependencyValidator()

    # Test case 1: All supported
    print("Test 1: All supported dependencies")
    result1 = validator.validate(["requests", "pandas", "json", "datetime"])
    print(get_validation_summary(result1))
    print()

    # Test case 2: Mixed supported/unsupported
    print("Test 2: Mixed dependencies")
    result2 = validator.validate(["requests", "unsupported_lib", "pandas", "fakepkg"])
    print(get_validation_summary(result2))
    print()

    # Test case 3: Get manual implementation guide
    print("Test 3: Manual implementation guide")
    guide = validator.get_manual_implementation_guide("unsupported_lib")
    print("Guide:", guide)
