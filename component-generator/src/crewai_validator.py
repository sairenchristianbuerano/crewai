"""
Validator for generated crewAI tool code
"""

import ast
import re
from typing import List, Set
import structlog

from base_classes import ValidationResult

logger = structlog.get_logger()


class CrewAIToolValidator:
    """Validates generated crewAI tool code for correctness and security"""

    # Required imports for crewAI tools
    REQUIRED_IMPORTS = {
        'crewai.tools',  # BaseTool
        'pydantic',      # BaseModel, Field
        'typing',        # Type hints
    }

    # Forbidden imports for security
    FORBIDDEN_IMPORTS = {
        'os.system',
        'subprocess.Popen',
        'eval',
        'exec',
        '__import__',
    }

    # Required BaseTool attributes
    REQUIRED_ATTRIBUTES = {
        'name',
        'description',
        'args_schema',
    }

    # Required methods
    REQUIRED_METHODS = {
        '_run',
        'run',
    }

    def __init__(self):
        self.logger = logger.bind(component="crewai_validator")

    def validate(self, code: str) -> ValidationResult:
        """
        Validate generated tool code

        Args:
            code: Generated Python code to validate

        Returns:
            ValidationResult with errors, warnings, and suggestions
        """
        errors = []
        warnings = []
        suggestions = []

        try:
            # 1. Check Python syntax
            syntax_errors = self._check_syntax(code)
            errors.extend(syntax_errors)

            if syntax_errors:
                # If syntax errors exist, can't do further validation
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    suggestions=["Fix syntax errors before proceeding"]
                )

            # 2. Parse AST for structural validation
            tree = ast.parse(code)

            # 3. Check imports
            import_errors, import_warnings = self._check_imports(tree)
            errors.extend(import_errors)
            warnings.extend(import_warnings)

            # 4. Check class structure
            class_errors, class_warnings, class_suggestions = self._check_class_structure(tree, code)
            errors.extend(class_errors)
            warnings.extend(class_warnings)
            suggestions.extend(class_suggestions)

            # 5. Check security issues
            security_errors, security_warnings = self._check_security(tree, code)
            errors.extend(security_errors)
            warnings.extend(security_warnings)

            # 6. Check BaseTool compliance
            basetool_errors, basetool_suggestions = self._check_basetool_compliance(tree, code)
            errors.extend(basetool_errors)
            suggestions.extend(basetool_suggestions)

            is_valid = len(errors) == 0

            self.logger.info(
                "Validation complete",
                is_valid=is_valid,
                errors_count=len(errors),
                warnings_count=len(warnings)
            )

            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )

        except Exception as e:
            self.logger.error("Validation failed", error=str(e))
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=warnings,
                suggestions=suggestions
            )

    def _check_syntax(self, code: str) -> List[str]:
        """Check Python syntax"""
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return errors

    def _check_imports(self, tree: ast.AST) -> tuple[List[str], List[str]]:
        """Check imports for required and forbidden modules"""
        errors = []
        warnings = []

        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        # Check for forbidden imports
        for forbidden in self.FORBIDDEN_IMPORTS:
            if any(forbidden in imp for imp in imports):
                errors.append(f"Forbidden import detected: {forbidden}")

        # Check for required imports (relaxed - just need BaseTool)
        if not any('BaseTool' in imp or 'crewai' in imp for imp in imports):
            errors.append("Missing required import: crewai.tools.BaseTool")

        return errors, warnings

    def _check_class_structure(self, tree: ast.AST, code: str) -> tuple[List[str], List[str], List[str]]:
        """Check class structure and organization"""
        errors = []
        warnings = []
        suggestions = []

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        if not classes:
            errors.append("No class definition found")
            return errors, warnings, suggestions

        # Find the main tool class (should inherit from BaseTool)
        tool_class = None
        for cls in classes:
            if any(base.id == 'BaseTool' if isinstance(base, ast.Name) else False for base in cls.bases):
                tool_class = cls
                break

        if not tool_class:
            errors.append("No class inheriting from BaseTool found")
            return errors, warnings, suggestions

        # Check for input schema class (should inherit from BaseModel)
        schema_classes = [
            cls for cls in classes
            if any(base.id == 'BaseModel' if isinstance(base, ast.Name) else False for base in cls.bases)
        ]

        if not schema_classes:
            warnings.append("No input schema class (BaseModel) found - tool may not have structured inputs")

        return errors, warnings, suggestions

    def _check_security(self, tree: ast.AST, code: str) -> tuple[List[str], List[str]]:
        """Check for security issues"""
        errors = []
        warnings = []

        # Check for dangerous function calls
        dangerous_functions = {'eval', 'exec', '__import__', 'compile'}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_functions:
                    errors.append(f"Dangerous function call detected: {node.func.id}")

        # Check for shell command execution
        if 'os.system' in code or 'subprocess.call' in code or 'subprocess.Popen' in code:
            warnings.append("Shell command execution detected - ensure proper input sanitization")

        return errors, warnings

    def _check_basetool_compliance(self, tree: ast.AST, code: str) -> tuple[List[str], List[str]]:
        """Check BaseTool interface compliance"""
        errors = []
        suggestions = []

        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        tool_class = None
        for cls in classes:
            if any(base.id == 'BaseTool' if isinstance(base, ast.Name) else False for base in cls.bases):
                tool_class = cls
                break

        if not tool_class:
            return errors, suggestions

        # Check for required attributes (as class variables)
        class_attrs = set()
        methods = set()

        for item in tool_class.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_attrs.add(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_attrs.add(target.id)
            elif isinstance(item, ast.FunctionDef):
                methods.add(item.name)

        # Check required attributes
        missing_attrs = self.REQUIRED_ATTRIBUTES - class_attrs
        if missing_attrs:
            errors.append(f"Missing required attributes: {', '.join(missing_attrs)}")

        # Check required methods
        missing_methods = self.REQUIRED_METHODS - methods
        if missing_methods:
            errors.append(f"Missing required methods: {', '.join(missing_methods)}")

        # Check if _run method has correct signature
        if '_run' in methods:
            run_method = next((m for m in tool_class.body if isinstance(m, ast.FunctionDef) and m.name == '_run'), None)
            if run_method and len(run_method.args.args) < 2:  # self + at least one param
                suggestions.append("_run method should accept input parameters")

        return errors, suggestions


class CrewAIFeasibilityChecker:
    """Assesses feasibility of generating a tool before attempting generation"""

    def __init__(self):
        self.logger = logger.bind(component="feasibility_checker")

    async def assess(self, spec_dict: dict, rag_context: dict = None) -> 'FeasibilityAssessment':
        """
        Assess whether tool generation is feasible

        Args:
            spec_dict: Tool specification as dictionary
            rag_context: Optional RAG context with similar patterns

        Returns:
            FeasibilityAssessment with confidence and issues
        """
        from base_classes import FeasibilityAssessment

        issues = []
        suggestions = []
        missing_info = []

        # Check required fields
        if not spec_dict.get('name'):
            missing_info.append("Tool name is required")

        if not spec_dict.get('description'):
            missing_info.append("Tool description is required")

        if not spec_dict.get('requirements') and not spec_dict.get('inputs'):
            missing_info.append("Either requirements or inputs should be specified")

        # Assess complexity
        complexity = "simple"
        if spec_dict.get('requirements'):
            num_requirements = len(spec_dict['requirements'])
            if num_requirements > 5:
                complexity = "complex"
            elif num_requirements > 2:
                complexity = "medium"

        # Check for similar patterns
        similar_patterns_found = 0
        if rag_context and rag_context.get('results'):
            similar_patterns_found = len(rag_context['results'])

        if similar_patterns_found == 0:
            suggestions.append("No similar patterns found - generation may be less accurate")

        # Determine confidence
        if missing_info:
            confidence = "blocked"
            feasible = False
        elif complexity == "complex" and similar_patterns_found == 0:
            confidence = "low"
            feasible = True
            suggestions.append("Complex tool with no patterns - consider simplifying or adding more detail")
        elif similar_patterns_found >= 2:
            confidence = "high"
            feasible = True
        else:
            confidence = "medium"
            feasible = True

        return FeasibilityAssessment(
            feasible=feasible,
            confidence=confidence,
            complexity=complexity,
            issues=issues,
            suggestions=suggestions,
            missing_info=missing_info,
            similar_patterns_found=similar_patterns_found
        )
