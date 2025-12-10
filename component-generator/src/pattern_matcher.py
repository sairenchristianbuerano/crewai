"""
Pattern Matcher for CrewAI Tool Generation

Compares generated tool code against official crewAI patterns to ensure
quality, consistency, and adherence to best practices.

Features:
- AST-based code structure comparison
- Pattern matching against official tools
- Quality suggestions and recommendations
- Compatibility checks

Author: CrewAI Tool Generator Team
Date: 2025-12-11
Phase: 4 - Pattern Validation
"""

import ast
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import structlog


logger = structlog.get_logger().bind(component="pattern_matcher")


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PatternMatchResult:
    """
    Result of pattern matching analysis

    Attributes:
        matches_pattern: True if code matches official patterns
        pattern_score: Similarity score (0-100)
        has_base_tool: True if inherits from BaseTool
        has_args_schema: True if defines args_schema
        has_run_method: True if implements _run() method
        has_docstrings: True if has comprehensive docstrings
        has_error_handling: True if includes try/except
        issues: List of issues found
        suggestions: List of improvement suggestions
        best_practices: List of best practices followed
        warnings: List of warnings
    """
    matches_pattern: bool
    pattern_score: int
    has_base_tool: bool
    has_args_schema: bool
    has_run_method: bool
    has_docstrings: bool
    has_error_handling: bool
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "matches_pattern": self.matches_pattern,
            "pattern_score": self.pattern_score,
            "checks": {
                "has_base_tool": self.has_base_tool,
                "has_args_schema": self.has_args_schema,
                "has_run_method": self.has_run_method,
                "has_docstrings": self.has_docstrings,
                "has_error_handling": self.has_error_handling
            },
            "issues": self.issues,
            "suggestions": self.suggestions,
            "best_practices": self.best_practices,
            "warnings": self.warnings
        }


# ============================================================================
# PATTERN MATCHER CLASS
# ============================================================================

class PatternMatcher:
    """
    Validates generated code against official crewAI patterns

    This matcher ensures generated tools follow official conventions:
    - Inherit from BaseTool
    - Define args_schema with Pydantic BaseModel
    - Implement _run() method
    - Include comprehensive docstrings
    - Handle errors gracefully
    - Follow PEP 8 style guide
    """

    def __init__(self):
        """Initialize the pattern matcher"""
        self.logger = structlog.get_logger().bind(component="pattern_matcher")
        self._load_official_patterns()

    def _load_official_patterns(self):
        """Load official pattern requirements"""
        # Official crewAI tool requirements
        self.official_requirements = {
            'required_base_class': 'BaseTool',
            'required_methods': ['_run'],
            'recommended_methods': ['run', '__init__', '_generate_description'],
            'required_imports': ['BaseTool', 'BaseModel', 'Field'],
            'required_attributes': ['name', 'description', 'args_schema'],
            'docstring_required': True,
            'type_hints_required': True,
            'error_handling_required': True
        }

    def analyze(self, code: str) -> PatternMatchResult:
        """
        Analyze code and compare against official patterns

        Args:
            code: Generated Python code to analyze

        Returns:
            PatternMatchResult with detailed analysis
        """
        self.logger.info("Starting pattern analysis")

        # Initialize result tracking
        issues = []
        suggestions = []
        best_practices = []
        warnings = []

        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return PatternMatchResult(
                matches_pattern=False,
                pattern_score=0,
                has_base_tool=False,
                has_args_schema=False,
                has_run_method=False,
                has_docstrings=False,
                has_error_handling=False,
                issues=[f"Syntax error: {str(e)}"],
                suggestions=["Fix syntax errors before validation"],
                best_practices=[],
                warnings=[]
            )

        # Perform checks
        has_base_tool = self._check_base_tool_inheritance(tree)
        has_args_schema = self._check_args_schema(tree)
        has_run_method = self._check_run_method(tree)
        has_docstrings = self._check_docstrings(tree)
        has_error_handling = self._check_error_handling(tree)

        # Check imports
        imports_valid, import_issues = self._check_imports(tree)
        issues.extend(import_issues)

        # Check type hints
        type_hints_valid, type_issues = self._check_type_hints(tree)
        suggestions.extend(type_issues)

        # Check class attributes
        attrs_valid, attr_issues = self._check_required_attributes(tree)
        issues.extend(attr_issues)

        # Calculate pattern score (0-100)
        pattern_score = self._calculate_pattern_score({
            'has_base_tool': has_base_tool,
            'has_args_schema': has_args_schema,
            'has_run_method': has_run_method,
            'has_docstrings': has_docstrings,
            'has_error_handling': has_error_handling,
            'imports_valid': imports_valid,
            'type_hints_valid': type_hints_valid,
            'attrs_valid': attrs_valid
        })

        # Determine if matches pattern (score >= 80)
        matches_pattern = pattern_score >= 80 and has_base_tool and has_run_method

        # Add suggestions based on score
        if pattern_score < 100:
            suggestions.extend(self._get_improvement_suggestions({
                'has_base_tool': has_base_tool,
                'has_args_schema': has_args_schema,
                'has_run_method': has_run_method,
                'has_docstrings': has_docstrings,
                'has_error_handling': has_error_handling
            }))

        # Identify best practices followed
        best_practices = self._identify_best_practices({
            'has_base_tool': has_base_tool,
            'has_args_schema': has_args_schema,
            'has_run_method': has_run_method,
            'has_docstrings': has_docstrings,
            'has_error_handling': has_error_handling
        })

        # Add warnings
        if not has_error_handling:
            warnings.append("No error handling detected - tool may fail ungracefully")
        if not has_docstrings:
            warnings.append("Missing docstrings - reduces code maintainability")

        result = PatternMatchResult(
            matches_pattern=matches_pattern,
            pattern_score=pattern_score,
            has_base_tool=has_base_tool,
            has_args_schema=has_args_schema,
            has_run_method=has_run_method,
            has_docstrings=has_docstrings,
            has_error_handling=has_error_handling,
            issues=issues,
            suggestions=suggestions,
            best_practices=best_practices,
            warnings=warnings
        )

        self.logger.info(
            "Pattern analysis completed",
            matches_pattern=matches_pattern,
            pattern_score=pattern_score
        )

        return result

    def _check_base_tool_inheritance(self, tree: ast.AST) -> bool:
        """Check if code defines a class that inherits from BaseTool"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseTool':
                        return True
        return False

    def _check_args_schema(self, tree: ast.AST) -> bool:
        """Check if code defines an args_schema attribute"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    # Check for args_schema attribute
                    if isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name) and item.target.id == 'args_schema':
                            return True
        return False

    def _check_run_method(self, tree: ast.AST) -> bool:
        """Check if code implements _run method"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == '_run':
                        return True
        return False

    def _check_docstrings(self, tree: ast.AST) -> bool:
        """Check if code has docstrings"""
        has_module_docstring = False
        has_class_docstring = False
        has_method_docstring = False

        # Check module docstring
        if isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            has_module_docstring = True

        # Check class and method docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if ast.get_docstring(node):
                    has_class_docstring = True

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if ast.get_docstring(item):
                            has_method_docstring = True

        # Return True if at least class and method docstrings exist
        return has_class_docstring and has_method_docstring

    def _check_error_handling(self, tree: ast.AST) -> bool:
        """Check if code includes error handling (try/except)"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                return True
        return False

    def _check_imports(self, tree: ast.AST) -> tuple[bool, List[str]]:
        """Check if required imports are present"""
        imported_names = set()
        issues = []

        # Extract all imported names
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name)

        # Check required imports
        required = set(self.official_requirements['required_imports'])
        missing = required - imported_names

        if missing:
            issues.append(f"Missing required imports: {', '.join(missing)}")
            return False, issues

        return True, issues

    def _check_type_hints(self, tree: ast.AST) -> tuple[bool, List[str]]:
        """Check if functions have type hints"""
        suggestions = []
        functions_without_hints = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip __init__ and private methods for now
                if node.name.startswith('_') and node.name != '_run':
                    continue

                # Check for return annotation
                if not node.returns:
                    functions_without_hints.append(node.name)

        if functions_without_hints:
            suggestions.append(
                f"Consider adding type hints to: {', '.join(functions_without_hints)}"
            )
            return False, suggestions

        return True, suggestions

    def _check_required_attributes(self, tree: ast.AST) -> tuple[bool, List[str]]:
        """Check if tool class has required attributes"""
        issues = []
        found_attributes = set()

        # Find tool class and extract attributes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's the tool class (inherits from BaseTool)
                is_tool_class = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseTool':
                        is_tool_class = True
                        break

                if is_tool_class:
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign):
                            if isinstance(item.target, ast.Name):
                                found_attributes.add(item.target.id)

        # Check required attributes
        required = set(self.official_requirements['required_attributes'])
        missing = required - found_attributes

        if missing:
            issues.append(f"Missing required attributes: {', '.join(missing)}")
            return False, issues

        return True, issues

    def _calculate_pattern_score(self, checks: Dict[str, bool]) -> int:
        """
        Calculate pattern matching score (0-100)

        Weights:
        - has_base_tool: 25 points (critical)
        - has_run_method: 25 points (critical)
        - has_args_schema: 15 points
        - has_docstrings: 10 points
        - has_error_handling: 10 points
        - imports_valid: 5 points
        - type_hints_valid: 5 points
        - attrs_valid: 5 points
        """
        score = 0

        if checks.get('has_base_tool', False):
            score += 25
        if checks.get('has_run_method', False):
            score += 25
        if checks.get('has_args_schema', False):
            score += 15
        if checks.get('has_docstrings', False):
            score += 10
        if checks.get('has_error_handling', False):
            score += 10
        if checks.get('imports_valid', False):
            score += 5
        if checks.get('type_hints_valid', False):
            score += 5
        if checks.get('attrs_valid', False):
            score += 5

        return score

    def _get_improvement_suggestions(self, checks: Dict[str, bool]) -> List[str]:
        """Get suggestions for improving pattern match"""
        suggestions = []

        if not checks.get('has_base_tool'):
            suggestions.append("Inherit from BaseTool class")
        if not checks.get('has_run_method'):
            suggestions.append("Implement _run() method")
        if not checks.get('has_args_schema'):
            suggestions.append("Define args_schema with Pydantic BaseModel")
        if not checks.get('has_docstrings'):
            suggestions.append("Add comprehensive docstrings to class and methods")
        if not checks.get('has_error_handling'):
            suggestions.append("Add try/except error handling in _run() method")

        return suggestions

    def _identify_best_practices(self, checks: Dict[str, bool]) -> List[str]:
        """Identify which best practices are being followed"""
        practices = []

        if checks.get('has_base_tool'):
            practices.append("✅ Inherits from BaseTool (official pattern)")
        if checks.get('has_args_schema'):
            practices.append("✅ Defines args_schema with Pydantic validation")
        if checks.get('has_run_method'):
            practices.append("✅ Implements _run() method (required)")
        if checks.get('has_docstrings'):
            practices.append("✅ Includes comprehensive docstrings")
        if checks.get('has_error_handling'):
            practices.append("✅ Includes error handling (robust)")

        return practices


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def quick_validate(code: str) -> bool:
    """
    Quick validation - returns True if code passes basic checks

    Args:
        code: Generated Python code

    Returns:
        True if code is valid
    """
    matcher = PatternMatcher()
    result = matcher.analyze(code)
    return result.matches_pattern


def get_pattern_report(result: PatternMatchResult) -> str:
    """
    Get human-readable pattern matching report

    Args:
        result: PatternMatchResult

    Returns:
        Formatted report string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("PATTERN VALIDATION REPORT")
    lines.append("=" * 60)

    # Score and status
    status = "✅ PASS" if result.matches_pattern else "❌ FAIL"
    lines.append(f"Status: {status}")
    lines.append(f"Pattern Score: {result.pattern_score}/100")
    lines.append("")

    # Checks
    lines.append("CHECKS:")
    lines.append(f"  {'✅' if result.has_base_tool else '❌'} Inherits from BaseTool")
    lines.append(f"  {'✅' if result.has_args_schema else '❌'} Defines args_schema")
    lines.append(f"  {'✅' if result.has_run_method else '❌'} Implements _run() method")
    lines.append(f"  {'✅' if result.has_docstrings else '❌'} Has docstrings")
    lines.append(f"  {'✅' if result.has_error_handling else '❌'} Has error handling")
    lines.append("")

    # Best practices
    if result.best_practices:
        lines.append("BEST PRACTICES FOLLOWED:")
        for practice in result.best_practices:
            lines.append(f"  {practice}")
        lines.append("")

    # Issues
    if result.issues:
        lines.append("ISSUES:")
        for issue in result.issues:
            lines.append(f"  ❌ {issue}")
        lines.append("")

    # Suggestions
    if result.suggestions:
        lines.append("SUGGESTIONS:")
        for suggestion in result.suggestions:
            lines.append(f"  💡 {suggestion}")
        lines.append("")

    # Warnings
    if result.warnings:
        lines.append("WARNINGS:")
        for warning in result.warnings:
            lines.append(f"  ⚠️  {warning}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage
    sample_code = """
from typing import Optional, Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SampleToolInputSchema(BaseModel):
    \"\"\"Input schema for SampleTool\"\"\"
    query: str = Field(..., description="Search query")

class SampleTool(BaseTool):
    \"\"\"Sample tool for testing\"\"\"
    name: str = "Sample Tool"
    description: str = "A sample tool for demonstration"
    args_schema: Type[BaseModel] = SampleToolInputSchema

    def _run(self, query: str) -> Any:
        \"\"\"Execute the tool\"\"\"
        try:
            result = {"query": query, "result": "success"}
            return result
        except Exception as e:
            return {"error": str(e)}
"""

    # Analyze code
    matcher = PatternMatcher()
    result = matcher.analyze(sample_code)

    # Print report
    print(get_pattern_report(result))
