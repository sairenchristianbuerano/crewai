"""
Code Quality Analyzer for CrewAI Tool Generator

Provides advanced code quality checks including:
- Code smell detection
- CrewAI-specific anti-pattern detection
- Complexity metrics
- Best practice validation

This complements the existing validator.py and pattern_matcher.py with deeper analysis.

Phase: 2.1 - Enhanced Code Quality Checks
Author: Component Factory
Date: 2025-12-21
"""

import ast
import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import structlog


logger = structlog.get_logger().bind(component="code_quality_analyzer")


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class QualityIssue:
    """
    Represents a code quality issue

    Attributes:
        severity: 'error', 'warning', or 'info'
        category: Type of issue (e.g., 'code_smell', 'anti_pattern', 'complexity')
        message: Human-readable description
        line_number: Line where issue occurs (if applicable)
        suggestion: Actionable fix suggestion
    """
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'code_smell', 'anti_pattern', 'complexity', 'best_practice'
    message: str
    line_number: int = None
    suggestion: str = None


@dataclass
class QualityMetrics:
    """
    Code quality metrics

    Attributes:
        overall_score: Overall quality score (0-100)
        complexity_score: Cyclomatic complexity score (0-100)
        maintainability_score: Code maintainability (0-100)
        issues_count: Total number of issues found
        code_smells: Number of code smells detected
        anti_patterns: Number of anti-patterns detected
        lines_of_code: Total lines of code
        comment_ratio: Ratio of comments to code
    """
    overall_score: int
    complexity_score: int
    maintainability_score: int
    issues_count: int
    code_smells: int
    anti_patterns: int
    lines_of_code: int
    comment_ratio: float


@dataclass
class QualityAnalysisResult:
    """
    Complete quality analysis result

    Attributes:
        is_high_quality: True if code meets high quality standards (score >= 80)
        metrics: QualityMetrics object
        issues: List of QualityIssue objects
        strengths: List of positive findings
        recommendations: Prioritized improvement recommendations
    """
    is_high_quality: bool
    metrics: QualityMetrics
    issues: List[QualityIssue] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "is_high_quality": self.is_high_quality,
            "metrics": {
                "overall_score": self.metrics.overall_score,
                "complexity_score": self.metrics.complexity_score,
                "maintainability_score": self.metrics.maintainability_score,
                "issues_count": self.metrics.issues_count,
                "code_smells": self.metrics.code_smells,
                "anti_patterns": self.metrics.anti_patterns,
                "lines_of_code": self.metrics.lines_of_code,
                "comment_ratio": self.metrics.comment_ratio
            },
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "message": issue.message,
                    "line_number": issue.line_number,
                    "suggestion": issue.suggestion
                }
                for issue in self.issues
            ],
            "strengths": self.strengths,
            "recommendations": self.recommendations
        }


# ============================================================================
# CODE QUALITY ANALYZER
# ============================================================================

class CodeQualityAnalyzer:
    """
    Analyzes generated code for quality issues, code smells, and anti-patterns

    This analyzer provides deep code quality analysis including:
    - Unused imports detection
    - Code complexity metrics
    - CrewAI-specific anti-patterns
    - Best practice violations
    - Maintainability issues
    """

    # Thresholds
    MAX_METHOD_LENGTH = 50  # lines
    MAX_PARAMETERS = 5
    MAX_COMPLEXITY = 10  # cyclomatic complexity per method
    MIN_COMMENT_RATIO = 0.15  # 15% comments to code ratio

    # CrewAI-specific anti-patterns
    BLOCKING_OPERATIONS = {
        'time.sleep', 'input', 'sleep',
        'requests.get', 'requests.post', 'requests.put', 'requests.delete',
        'urllib.request.urlopen',
    }

    STATEFUL_PATTERNS = {
        'global ', 'nonlocal ',
    }

    def __init__(self):
        """Initialize the code quality analyzer"""
        self.logger = logger.bind(component="code_quality_analyzer")

    def analyze(self, code: str) -> QualityAnalysisResult:
        """
        Perform comprehensive quality analysis on code

        Args:
            code: Python source code to analyze

        Returns:
            QualityAnalysisResult with detailed quality information
        """
        self.logger.info("Starting code quality analysis")

        issues = []
        strengths = []

        # Parse code
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
        except SyntaxError as e:
            return QualityAnalysisResult(
                is_high_quality=False,
                metrics=QualityMetrics(
                    overall_score=0,
                    complexity_score=0,
                    maintainability_score=0,
                    issues_count=1,
                    code_smells=0,
                    anti_patterns=0,
                    lines_of_code=len(code.split('\n')),
                    comment_ratio=0.0
                ),
                issues=[QualityIssue(
                    severity='error',
                    category='syntax',
                    message=f"Syntax error: {str(e)}",
                    line_number=e.lineno,
                    suggestion="Fix syntax errors before quality analysis"
                )],
                strengths=[],
                recommendations=["Fix syntax errors first"]
            )

        # Run all quality checks
        issues.extend(self._check_unused_imports(tree, code))
        issues.extend(self._check_code_complexity(tree))
        issues.extend(self._check_method_length(tree, lines))
        issues.extend(self._check_parameter_count(tree))
        issues.extend(self._check_magic_numbers(tree))
        issues.extend(self._check_naming_conventions(tree))
        issues.extend(self._check_crewai_anti_patterns(tree, code))
        issues.extend(self._check_error_handling_quality(tree))
        issues.extend(self._check_resource_management(tree, code))

        # Calculate metrics
        metrics = self._calculate_metrics(tree, code, issues)

        # Identify strengths
        strengths = self._identify_strengths(tree, code, issues)

        # Generate prioritized recommendations
        recommendations = self._generate_recommendations(issues, metrics)

        # Determine if high quality (score >= 80)
        is_high_quality = metrics.overall_score >= 80

        result = QualityAnalysisResult(
            is_high_quality=is_high_quality,
            metrics=metrics,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations
        )

        self.logger.info(
            "Quality analysis complete",
            overall_score=metrics.overall_score,
            issues_count=len(issues),
            is_high_quality=is_high_quality
        )

        return result

    def _check_unused_imports(self, tree: ast.AST, code: str) -> List[QualityIssue]:
        """Detect unused imports"""
        issues = []

        # Collect all imports
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = node.lineno

        # Check usage of each import
        for import_name, line_no in imports.items():
            # Skip special imports that might be used dynamically
            if import_name in ('Type', 'Any', 'Optional', 'List', 'Dict', 'Union', 'Tuple', 'Set'):
                continue  # Type hints are often used in annotations

            # Check if import is used in code
            # Simple heuristic: check if name appears outside import statement
            pattern = re.compile(r'\b' + re.escape(import_name) + r'\b')
            matches = list(pattern.finditer(code))

            # Filter out the import line itself
            code_lines = code.split('\n')
            import_line = code_lines[line_no - 1] if line_no > 0 else ""

            # Count uses outside of import statement
            uses = 0
            for match in matches:
                # Get line number of match
                match_line_no = code[:match.start()].count('\n') + 1
                if match_line_no != line_no:
                    uses += 1

            if uses == 0:
                issues.append(QualityIssue(
                    severity='info',
                    category='code_smell',
                    message=f"Unused import: '{import_name}'",
                    line_number=line_no,
                    suggestion=f"Remove unused import '{import_name}' to keep code clean"
                ))

        return issues

    def _check_code_complexity(self, tree: ast.AST) -> List[QualityIssue]:
        """Check cyclomatic complexity of methods"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)

                if complexity > self.MAX_COMPLEXITY:
                    issues.append(QualityIssue(
                        severity='warning',
                        category='complexity',
                        message=f"Method '{node.name}' has high complexity ({complexity})",
                        line_number=node.lineno,
                        suggestion=f"Consider breaking '{node.name}' into smaller methods (target complexity: {self.MAX_COMPLEXITY})"
                    ))

        return issues

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Start with 1

        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _check_method_length(self, tree: ast.AST, lines: List[str]) -> List[QualityIssue]:
        """Check for overly long methods"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate method length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    method_length = node.end_lineno - node.lineno + 1

                    if method_length > self.MAX_METHOD_LENGTH:
                        issues.append(QualityIssue(
                            severity='info',
                            category='maintainability',
                            message=f"Method '{node.name}' is too long ({method_length} lines)",
                            line_number=node.lineno,
                            suggestion=f"Consider breaking '{node.name}' into smaller methods (target: <{self.MAX_METHOD_LENGTH} lines)"
                        ))

        return issues

    def _check_parameter_count(self, tree: ast.AST) -> List[QualityIssue]:
        """Check for methods with too many parameters"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (excluding self)
                param_count = len(node.args.args)
                if node.args.args and node.args.args[0].arg == 'self':
                    param_count -= 1

                if param_count > self.MAX_PARAMETERS:
                    issues.append(QualityIssue(
                        severity='warning',
                        category='code_smell',
                        message=f"Method '{node.name}' has too many parameters ({param_count})",
                        line_number=node.lineno,
                        suggestion=f"Consider using a parameter object or reducing parameters in '{node.name}'"
                    ))

        return issues

    def _check_magic_numbers(self, tree: ast.AST) -> List[QualityIssue]:
        """Detect magic numbers (unexplained numeric constants)"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                # Check for numeric constants that aren't 0, 1, -1
                if isinstance(node.value, (int, float)):
                    if node.value not in (0, 1, -1, 0.0, 1.0):
                        # Skip if it's a default value in Field() or similar
                        parent = getattr(node, 'parent', None)
                        if not self._is_acceptable_magic_number_context(node):
                            issues.append(QualityIssue(
                                severity='info',
                                category='code_smell',
                                message=f"Magic number detected: {node.value}",
                                line_number=node.lineno,
                                suggestion=f"Consider defining {node.value} as a named constant for clarity"
                            ))

        return issues

    def _is_acceptable_magic_number_context(self, node: ast.Constant) -> bool:
        """Check if magic number is in acceptable context (e.g., Field default)"""
        # This is a simplified check - in production would need parent tracking
        # For now, we'll be lenient with magic numbers
        return True

    def _check_naming_conventions(self, tree: ast.AST) -> List[QualityIssue]:
        """Check naming convention compliance"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check snake_case for functions
                if not re.match(r'^_?[a-z][a-z0-9_]*$', node.name):
                    if node.name not in ('__init__', '__str__', '__repr__'):
                        issues.append(QualityIssue(
                            severity='info',
                            category='code_smell',
                            message=f"Function '{node.name}' doesn't follow snake_case convention",
                            line_number=node.lineno,
                            suggestion=f"Rename '{node.name}' to follow snake_case convention"
                        ))

            elif isinstance(node, ast.ClassDef):
                # Check PascalCase for classes
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(QualityIssue(
                        severity='info',
                        category='code_smell',
                        message=f"Class '{node.name}' doesn't follow PascalCase convention",
                        line_number=node.lineno,
                        suggestion=f"Rename '{node.name}' to follow PascalCase convention"
                    ))

        return issues

    def _check_crewai_anti_patterns(self, tree: ast.AST, code: str) -> List[QualityIssue]:
        """Check for CrewAI-specific anti-patterns"""
        issues = []

        # Check for blocking operations in _run method
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '_run':
                # Check for blocking calls
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        call_name = self._get_call_name(child)
                        if call_name in self.BLOCKING_OPERATIONS:
                            issues.append(QualityIssue(
                                severity='warning',
                                category='anti_pattern',
                                message=f"Blocking operation '{call_name}' in _run() method",
                                line_number=child.lineno,
                                suggestion=f"Consider using async version or adding timeout for '{call_name}'"
                            ))

        # Check for global state
        if any(pattern in code for pattern in self.STATEFUL_PATTERNS):
            issues.append(QualityIssue(
                severity='warning',
                category='anti_pattern',
                message="Global or nonlocal state detected",
                suggestion="Tools should be stateless - avoid global/nonlocal state"
            ))

        # Check for class-level mutable defaults
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.AnnAssign):
                        if isinstance(item.value, (ast.List, ast.Dict, ast.Set)):
                            issues.append(QualityIssue(
                                severity='warning',
                                category='anti_pattern',
                                message=f"Mutable class variable detected",
                                line_number=item.lineno,
                                suggestion="Avoid mutable class variables - use instance variables in __init__"
                            ))

        return issues

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract the full name of a function call"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Handle module.function calls
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            return '.'.join(parts)
        return ""

    def _check_error_handling_quality(self, tree: ast.AST) -> List[QualityIssue]:
        """Check error handling quality"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check for bare except
                if node.type is None:
                    issues.append(QualityIssue(
                        severity='warning',
                        category='best_practice',
                        message="Bare except clause detected",
                        line_number=node.lineno,
                        suggestion="Catch specific exceptions instead of using bare 'except:'"
                    ))

                # Check for empty except blocks
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append(QualityIssue(
                        severity='warning',
                        category='best_practice',
                        message="Empty except block (pass only)",
                        line_number=node.lineno,
                        suggestion="Add proper error handling or logging instead of silently passing"
                    ))

        return issues

    def _check_resource_management(self, tree: ast.AST, code: str) -> List[QualityIssue]:
        """Check for proper resource management"""
        issues = []

        # Check for file operations without 'with' statement
        has_open_call = False
        has_with_statement = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node)
                if call_name == 'open':
                    has_open_call = True
                    # Check if it's inside a 'with' statement
                    # This is simplified - full check would need parent tracking

            if isinstance(node, ast.With):
                has_with_statement = True

        if has_open_call and not has_with_statement:
            issues.append(QualityIssue(
                severity='warning',
                category='best_practice',
                message="File operation without context manager",
                suggestion="Use 'with open(...)' to ensure files are properly closed"
            ))

        return issues

    def _calculate_metrics(self, tree: ast.AST, code: str, issues: List[QualityIssue]) -> QualityMetrics:
        """Calculate quality metrics"""
        lines = code.split('\n')
        lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('#')])

        # Count comments
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        comment_ratio = comment_lines / lines_of_code if lines_of_code > 0 else 0

        # Count issue types
        code_smells = len([i for i in issues if i.category == 'code_smell'])
        anti_patterns = len([i for i in issues if i.category == 'anti_pattern'])

        # Calculate complexity score (0-100, inverse of average complexity)
        complexities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexities.append(self._calculate_cyclomatic_complexity(node))

        avg_complexity = sum(complexities) / len(complexities) if complexities else 1
        complexity_score = max(0, min(100, int(100 - (avg_complexity - 1) * 10)))

        # Calculate maintainability score based on various factors
        maintainability_score = 100

        # Reduce for long methods
        long_methods = len([i for i in issues if i.category == 'maintainability'])
        maintainability_score -= long_methods * 5

        # Reduce for low comment ratio
        if comment_ratio < self.MIN_COMMENT_RATIO:
            maintainability_score -= 10

        # Reduce for code smells
        maintainability_score -= code_smells * 2

        maintainability_score = max(0, min(100, maintainability_score))

        # Calculate overall score
        error_penalty = len([i for i in issues if i.severity == 'error']) * 20
        warning_penalty = len([i for i in issues if i.severity == 'warning']) * 5
        info_penalty = len([i for i in issues if i.severity == 'info']) * 2

        overall_score = 100 - error_penalty - warning_penalty - info_penalty
        overall_score = max(0, min(100, overall_score))

        return QualityMetrics(
            overall_score=overall_score,
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            issues_count=len(issues),
            code_smells=code_smells,
            anti_patterns=anti_patterns,
            lines_of_code=lines_of_code,
            comment_ratio=round(comment_ratio, 2)
        )

    def _identify_strengths(self, tree: ast.AST, code: str, issues: List[QualityIssue]) -> List[str]:
        """Identify code strengths"""
        strengths = []

        # Check for type hints
        has_type_hints = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    has_type_hints = True
                    break

        if has_type_hints:
            strengths.append("✅ Uses type hints for better code documentation")

        # Check for docstrings
        has_docstrings = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                if ast.get_docstring(node):
                    has_docstrings = True
                    break

        if has_docstrings:
            strengths.append("✅ Includes docstrings for documentation")

        # Check for error handling
        has_error_handling = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                has_error_handling = True
                break

        if has_error_handling:
            strengths.append("✅ Implements error handling")

        # Check complexity
        low_complexity = True
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._calculate_cyclomatic_complexity(node) > self.MAX_COMPLEXITY:
                    low_complexity = False
                    break

        if low_complexity:
            strengths.append("✅ Methods have low complexity")

        # Check for no anti-patterns
        has_anti_patterns = any(i.category == 'anti_pattern' for i in issues)
        if not has_anti_patterns:
            strengths.append("✅ No CrewAI anti-patterns detected")

        return strengths

    def _generate_recommendations(self, issues: List[QualityIssue], metrics: QualityMetrics) -> List[str]:
        """Generate prioritized improvement recommendations"""
        recommendations = []

        # Prioritize by severity
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        infos = [i for i in issues if i.severity == 'info']

        # Add error recommendations first
        if errors:
            recommendations.append(f"🔴 CRITICAL: Fix {len(errors)} error(s) first")
            for issue in errors[:3]:  # Top 3
                if issue.suggestion:
                    recommendations.append(f"   → {issue.suggestion}")

        # Add warning recommendations
        if warnings:
            recommendations.append(f"🟡 HIGH: Address {len(warnings)} warning(s)")
            # Group by category
            warning_categories = defaultdict(list)
            for w in warnings:
                warning_categories[w.category].append(w)

            for category, items in warning_categories.items():
                if items[0].suggestion:
                    recommendations.append(f"   → {items[0].suggestion}")

        # Add info recommendations
        if infos and metrics.overall_score < 90:
            recommendations.append(f"🟢 IMPROVE: Consider {len(infos)} enhancement(s)")

        # Add metric-based recommendations
        if metrics.complexity_score < 70:
            recommendations.append("💡 Reduce method complexity for better maintainability")

        if metrics.comment_ratio < self.MIN_COMMENT_RATIO:
            recommendations.append("💡 Add more comments to improve code documentation")

        if not recommendations:
            recommendations.append("✨ Code quality is excellent - no recommendations")

        return recommendations


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def analyze_code_quality(code: str) -> QualityAnalysisResult:
    """
    Quick quality analysis function

    Args:
        code: Python source code

    Returns:
        QualityAnalysisResult
    """
    analyzer = CodeQualityAnalyzer()
    return analyzer.analyze(code)


def get_quality_report(result: QualityAnalysisResult) -> str:
    """
    Generate human-readable quality report

    Args:
        result: QualityAnalysisResult

    Returns:
        Formatted report string
    """
    lines = []
    lines.append("=" * 70)
    lines.append("CODE QUALITY ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append("")

    # Overall status
    status = "✅ HIGH QUALITY" if result.is_high_quality else "⚠️  NEEDS IMPROVEMENT"
    lines.append(f"Status: {status}")
    lines.append(f"Overall Score: {result.metrics.overall_score}/100")
    lines.append("")

    # Metrics
    lines.append("METRICS:")
    lines.append(f"  Complexity Score: {result.metrics.complexity_score}/100")
    lines.append(f"  Maintainability Score: {result.metrics.maintainability_score}/100")
    lines.append(f"  Lines of Code: {result.metrics.lines_of_code}")
    lines.append(f"  Comment Ratio: {result.metrics.comment_ratio:.0%}")
    lines.append(f"  Total Issues: {result.metrics.issues_count}")
    lines.append(f"    - Code Smells: {result.metrics.code_smells}")
    lines.append(f"    - Anti-Patterns: {result.metrics.anti_patterns}")
    lines.append("")

    # Strengths
    if result.strengths:
        lines.append("STRENGTHS:")
        for strength in result.strengths:
            lines.append(f"  {strength}")
        lines.append("")

    # Issues by severity
    errors = [i for i in result.issues if i.severity == 'error']
    warnings = [i for i in result.issues if i.severity == 'warning']
    infos = [i for i in result.issues if i.severity == 'info']

    if errors:
        lines.append("ERRORS:")
        for issue in errors:
            lines.append(f"  ❌ {issue.message}")
            if issue.suggestion:
                lines.append(f"     💡 {issue.suggestion}")
        lines.append("")

    if warnings:
        lines.append("WARNINGS:")
        for issue in warnings[:5]:  # Top 5
            lines.append(f"  ⚠️  {issue.message}")
            if issue.suggestion:
                lines.append(f"     💡 {issue.suggestion}")
        if len(warnings) > 5:
            lines.append(f"  ... and {len(warnings) - 5} more warnings")
        lines.append("")

    if infos and result.metrics.overall_score < 90:
        lines.append("SUGGESTIONS:")
        for issue in infos[:3]:  # Top 3
            lines.append(f"  ℹ️  {issue.message}")
        if len(infos) > 3:
            lines.append(f"  ... and {len(infos) - 3} more suggestions")
        lines.append("")

    # Recommendations
    if result.recommendations:
        lines.append("RECOMMENDATIONS:")
        for rec in result.recommendations:
            lines.append(f"  {rec}")
        lines.append("")

    lines.append("=" * 70)

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
import time

class SampleToolInputSchema(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(100, description="Maximum results")

class SampleTool(BaseTool):
    \"\"\"Sample tool for testing\"\"\"
    name: str = "Sample Tool"
    description: str = "A sample tool"
    args_schema: Type[BaseModel] = SampleToolInputSchema

    def _run(self, query: str, max_results: int = 100) -> Any:
        try:
            time.sleep(5)  # Blocking operation
            result = {"query": query, "results": max_results}
            return result
        except:
            return {"error": "failed"}
"""

    # Analyze
    result = analyze_code_quality(sample_code)

    # Print report
    print(get_quality_report(result))
