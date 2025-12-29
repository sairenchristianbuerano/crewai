"""
Error tracking and learning system for the component generator.

Tracks validation errors across generation attempts to improve future generations
by learning from common mistakes and patterns.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class ErrorPattern:
    """Represents a tracked error pattern"""

    def __init__(self, error_type: str, error_message: str, solution: str):
        self.error_type = error_type
        self.error_message = error_message
        self.solution = solution
        self.frequency = 1
        self.last_seen = datetime.now().isoformat()
        self.tool_contexts = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "solution": self.solution,
            "frequency": self.frequency,
            "last_seen": self.last_seen,
            "tool_contexts": self.tool_contexts[:10]  # Keep last 10
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorPattern':
        """Create from dictionary"""
        pattern = cls(
            error_type=data["error_type"],
            error_message=data["error_message"],
            solution=data["solution"]
        )
        pattern.frequency = data.get("frequency", 1)
        pattern.last_seen = data.get("last_seen", datetime.now().isoformat())
        pattern.tool_contexts = data.get("tool_contexts", [])
        return pattern


class ErrorTracker:
    """Tracks and analyzes generation errors to improve future attempts"""

    # Error type to solution mapping
    ERROR_SOLUTIONS = {
        "dangerous_function_eval": "Use AST-based evaluation with ast.parse() instead of eval()",
        "dangerous_function_exec": "Use specific execution methods instead of exec()",
        "dangerous_function_compile": "Use ast.parse() for safe code analysis instead of compile()",
        "pydantic_attribute": "Create helper instances in _run() method, not in __init__()",
        "missing_import": "Ensure all required imports are at the top of the file",
        "undefined_variable": "Define all variables before use or pass them as parameters",
        "missing_method": "Implement required BaseTool methods: _run()",
        "invalid_syntax": "Check Python syntax, proper indentation, and bracket matching",
        "type_error": "Add proper type hints and ensure type compatibility",
    }

    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = data_dir
        self.error_file = os.path.join(data_dir, "error_patterns.json")
        self.logger = logger.bind(component="error_tracker")
        self.errors: Dict[str, ErrorPattern] = {}
        self._load_errors()

    def _load_errors(self):
        """Load error patterns from disk"""
        try:
            if os.path.exists(self.error_file):
                with open(self.error_file, 'r') as f:
                    data = json.load(f)
                    for error_data in data.get("errors", []):
                        pattern = ErrorPattern.from_dict(error_data)
                        key = self._make_key(pattern.error_type, pattern.error_message)
                        self.errors[key] = pattern
                self.logger.info("Error patterns loaded", count=len(self.errors))
            else:
                self.logger.info("No existing error patterns file found, starting fresh")
        except Exception as e:
            self.logger.error("Failed to load error patterns", error=str(e))

    def _save_errors(self):
        """Save error patterns to disk"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            data = {
                "errors": [pattern.to_dict() for pattern in self.errors.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.error_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.debug("Error patterns saved", count=len(self.errors))
        except Exception as e:
            self.logger.error("Failed to save error patterns", error=str(e))

    def _make_key(self, error_type: str, error_message: str) -> str:
        """Create a unique key for an error pattern"""
        # Normalize the error message to group similar errors
        normalized = error_message.lower().strip()
        return f"{error_type}:{normalized[:100]}"

    def _classify_error(self, error_message: str) -> str:
        """Classify error type from error message"""
        error_lower = error_message.lower()

        if "dangerous function call detected: eval" in error_lower:
            return "dangerous_function_eval"
        elif "dangerous function call detected: exec" in error_lower:
            return "dangerous_function_exec"
        elif "dangerous function call detected: compile" in error_lower:
            return "dangerous_function_compile"
        elif "has no field" in error_lower or "has no attribute" in error_lower:
            return "pydantic_attribute"
        elif "is not defined" in error_lower or "undefined" in error_lower:
            return "undefined_variable"
        elif "no module named" in error_lower or "cannot import" in error_lower:
            return "missing_import"
        elif "missing required method" in error_lower or "_run" in error_lower:
            return "missing_method"
        elif "invalid syntax" in error_lower or "syntaxerror" in error_lower:
            return "invalid_syntax"
        elif "type" in error_lower and "error" in error_lower:
            return "type_error"
        else:
            return "unknown"

    def track_error(
        self,
        errors: List[str],
        tool_name: str,
        attempt: int
    ):
        """
        Track validation errors from a generation attempt

        Args:
            errors: List of error messages from validation
            tool_name: Name of the tool being generated
            attempt: Which generation attempt (1-5)
        """
        for error_message in errors:
            error_type = self._classify_error(error_message)
            key = self._make_key(error_type, error_message)

            if key in self.errors:
                # Increment existing error
                pattern = self.errors[key]
                pattern.frequency += 1
                pattern.last_seen = datetime.now().isoformat()
                if tool_name not in pattern.tool_contexts:
                    pattern.tool_contexts.append(tool_name)
                    pattern.tool_contexts = pattern.tool_contexts[-10:]  # Keep last 10
            else:
                # Create new error pattern
                solution = self.ERROR_SOLUTIONS.get(error_type, "Review the error message and fix accordingly")
                pattern = ErrorPattern(error_type, error_message, solution)
                pattern.tool_contexts.append(tool_name)
                self.errors[key] = pattern

            self.logger.info(
                "Error tracked",
                error_type=error_type,
                tool_name=tool_name,
                attempt=attempt,
                frequency=pattern.frequency
            )

        # Save after each tracking
        self._save_errors()

    def get_top_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequent errors for prompt injection

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of error dictionaries sorted by frequency
        """
        sorted_errors = sorted(
            self.errors.values(),
            key=lambda x: x.frequency,
            reverse=True
        )

        return [
            {
                "type": pattern.error_type,
                "message": pattern.error_message,
                "solution": pattern.solution,
                "frequency": pattern.frequency
            }
            for pattern in sorted_errors[:limit]
        ]

    def get_analytics(self) -> Dict[str, Any]:
        """
        Get error analytics for the optional endpoint

        Returns:
            Dictionary with error statistics and trends
        """
        total_errors = sum(p.frequency for p in self.errors.values())

        # Group by error type
        type_counts = defaultdict(int)
        for pattern in self.errors.values():
            type_counts[pattern.error_type] += pattern.frequency

        # Get top errors
        top_errors = self.get_top_errors(limit=10)

        return {
            "total_tracked_errors": total_errors,
            "unique_error_patterns": len(self.errors),
            "errors_by_type": dict(type_counts),
            "top_errors": top_errors,
            "last_updated": max(
                (p.last_seen for p in self.errors.values()),
                default=None
            )
        }

    def clear_old_errors(self, days: int = 30):
        """
        Clear error patterns older than specified days

        Args:
            days: Number of days to keep
        """
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        initial_count = len(self.errors)
        self.errors = {
            k: v for k, v in self.errors.items()
            if v.last_seen > cutoff
        }

        removed = initial_count - len(self.errors)
        if removed > 0:
            self.logger.info(f"Cleared {removed} old error patterns")
            self._save_errors()
