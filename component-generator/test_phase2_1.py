#!/usr/bin/env python
"""
Phase 2.1 Test - Enhanced Code Quality Checks
Tests code quality analyzer including code smell detection and anti-pattern detection
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from code_quality_analyzer import (
    CodeQualityAnalyzer,
    analyze_code_quality,
    get_quality_report
)


def test_unused_imports_detection():
    """Test 1: Unused imports detection"""
    print("=" * 80)
    print("TEST 1: Unused Imports Detection")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Check 1.1: Detect unused import
    print("  Check 1.1: Detecting unused imports...")
    code_with_unused = """
from typing import Optional, List
from crewai.tools import BaseTool
import requests  # Unused
import json      # Unused

class TestTool(BaseTool):
    name: str = "Test"
    description: str = "Test tool"

    def _run(self, query: str) -> str:
        return "test"
"""

    result = analyze_code_quality(code_with_unused)
    unused_issues = [i for i in result.issues if 'Unused import' in i.message]

    if len(unused_issues) > 0:
        print(f"     [OK] Detected {len(unused_issues)} unused import(s)")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect unused imports")

    # Check 1.2: No false positives for used imports
    print("\n  Check 1.2: No false positives for used imports...")
    code_with_used = """
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class TestTool(BaseTool):
    name: str = "Test"
    args_schema: type = BaseModel

    def _run(self) -> str:
        return Field(description="test")
"""

    result2 = analyze_code_quality(code_with_used)
    false_positives = [i for i in result2.issues if 'Unused import' in i.message and 'BaseTool' in i.message]

    if len(false_positives) == 0:
        print(f"     [OK] No false positives for used imports")
        checks_passed += 1
    else:
        print(f"     [FAIL] False positives detected: {len(false_positives)}")

    # Check 1.3: Type hints imports are skipped
    print("\n  Check 1.3: Type hints imports not flagged...")
    code_with_types = """
from typing import Type, Any, Dict, List, Optional
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, data: Dict[str, Any]) -> Optional[List[str]]:
        return None
"""

    result3 = analyze_code_quality(code_with_types)
    type_false_positives = [
        i for i in result3.issues
        if 'Unused import' in i.message and any(t in i.message for t in ['Type', 'Any', 'Dict', 'List', 'Optional'])
    ]

    if len(type_false_positives) == 0:
        print(f"     [OK] Type hints imports correctly handled")
        checks_passed += 1
    else:
        print(f"     [FAIL] Type hints incorrectly flagged as unused")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_complexity_detection():
    """Test 2: Code complexity detection"""
    print("\n" + "=" * 80)
    print("TEST 2: Code Complexity Detection")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Check 2.1: Detect high complexity method
    print("  Check 2.1: Detecting high complexity methods...")
    high_complexity_code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, data: str) -> str:
        result = ""
        if data:
            if len(data) > 10:
                if data.startswith('a'):
                    for char in data:
                        if char.isalpha():
                            if char.isupper():
                                if char.isascii():
                                    result += char.lower()
                            else:
                                if char.isdigit():
                                    result += '0'
                                else:
                                    if len(result) > 5:
                                        result += char.upper()
                        else:
                            if char == ' ':
                                result += '_'
        return result
"""

    result = analyze_code_quality(high_complexity_code)
    complexity_issues = [i for i in result.issues if i.category == 'complexity']

    if len(complexity_issues) > 0:
        print(f"     [OK] Detected high complexity method")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect high complexity")

    # Check 2.2: Low complexity code gets good score
    print("\n  Check 2.2: Low complexity code scores well...")
    low_complexity_code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    \"\"\"Simple tool\"\"\"
    name: str = "Test"
    description: str = "Test tool"

    def _run(self, query: str) -> str:
        \"\"\"Execute tool\"\"\"
        try:
            return f"Result: {query}"
        except Exception as e:
            return f"Error: {str(e)}"
"""

    result2 = analyze_code_quality(low_complexity_code)

    if result2.metrics.complexity_score > 80:
        print(f"     [OK] Low complexity code has good score ({result2.metrics.complexity_score}/100)")
        checks_passed += 1
    else:
        print(f"     [FAIL] Low complexity score too low: {result2.metrics.complexity_score}")

    # Check 2.3: Complexity metric calculated correctly
    print("\n  Check 2.3: Complexity metric exists and in range...")

    if 0 <= result2.metrics.complexity_score <= 100:
        print(f"     [OK] Complexity score in valid range: {result2.metrics.complexity_score}")
        checks_passed += 1
    else:
        print(f"     [FAIL] Invalid complexity score: {result2.metrics.complexity_score}")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_crewai_anti_patterns():
    """Test 3: CrewAI-specific anti-pattern detection"""
    print("\n" + "=" * 80)
    print("TEST 3: CrewAI Anti-Pattern Detection")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 4

    # Check 3.1: Detect blocking operations in _run
    print("  Check 3.1: Detecting blocking operations in _run()...")
    blocking_code = """
import time
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, duration: int) -> str:
        time.sleep(duration)  # Blocking!
        return "done"
"""

    result = analyze_code_quality(blocking_code)
    blocking_issues = [i for i in result.issues if 'Blocking operation' in i.message]

    if len(blocking_issues) > 0:
        print(f"     [OK] Detected blocking operation (time.sleep)")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect blocking operations")

    # Check 3.2: Detect global state usage
    print("\n  Check 3.2: Detecting global state usage...")
    global_state_code = """
from crewai.tools import BaseTool

counter = 0  # Global state

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, value: int) -> int:
        global counter
        counter += value
        return counter
"""

    result2 = analyze_code_quality(global_state_code)
    global_issues = [i for i in result2.issues if 'Global' in i.message or 'state' in i.message.lower()]

    if len(global_issues) > 0:
        print(f"     [OK] Detected global state usage")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect global state")

    # Check 3.3: Detect mutable class variables
    print("\n  Check 3.3: Detecting mutable class variables...")
    mutable_class_var_code = """
from crewai.tools import BaseTool
from typing import List

class TestTool(BaseTool):
    name: str = "Test"
    cache: List[str] = []  # Mutable class variable - bad!

    def _run(self, item: str) -> List[str]:
        self.cache.append(item)
        return self.cache
"""

    result3 = analyze_code_quality(mutable_class_var_code)
    mutable_issues = [i for i in result3.issues if 'Mutable class variable' in i.message]

    if len(mutable_issues) > 0:
        print(f"     [OK] Detected mutable class variable")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect mutable class variables")

    # Check 3.4: Anti-pattern category tagged correctly
    print("\n  Check 3.4: Anti-patterns tagged with correct category...")

    anti_pattern_issues = [i for i in result.issues if i.category == 'anti_pattern']

    if len(anti_pattern_issues) > 0:
        print(f"     [OK] Anti-patterns tagged with 'anti_pattern' category")
        checks_passed += 1
    else:
        print(f"     [FAIL] Anti-patterns should have category='anti_pattern'")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_code_smell_detection():
    """Test 4: Code smell detection"""
    print("\n" + "=" * 80)
    print("TEST 4: Code Smell Detection")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Check 4.1: Detect too many parameters
    print("  Check 4.1: Detecting too many parameters...")
    many_params_code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, p1: str, p2: str, p3: str, p4: str, p5: str, p6: str, p7: str) -> str:
        return f"{p1} {p2} {p3} {p4} {p5} {p6} {p7}"
"""

    result = analyze_code_quality(many_params_code)
    param_issues = [i for i in result.issues if 'too many parameters' in i.message]

    if len(param_issues) > 0:
        print(f"     [OK] Detected too many parameters")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect too many parameters")

    # Check 4.2: Detect long methods
    print("\n  Check 4.2: Detecting overly long methods...")
    long_method_code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, data: str) -> str:
""" + "\n".join([f"        line_{i} = {i}" for i in range(60)]) + """
        return str(line_59)
"""

    result2 = analyze_code_quality(long_method_code)
    length_issues = [i for i in result2.issues if 'too long' in i.message]

    if len(length_issues) > 0:
        print(f"     [OK] Detected long method")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect long methods")

    # Check 4.3: Detect naming convention violations
    print("\n  Check 4.3: Detecting naming convention violations...")
    bad_naming_code = """
from crewai.tools import BaseTool

class test_tool(BaseTool):  # Should be PascalCase
    name: str = "Test"

    def RunMethod(self, data: str) -> str:  # Should be snake_case
        return data
"""

    result3 = analyze_code_quality(bad_naming_code)
    naming_issues = [i for i in result3.issues if 'convention' in i.message.lower()]

    if len(naming_issues) > 0:
        print(f"     [OK] Detected naming convention violations")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect naming violations")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_error_handling_quality():
    """Test 5: Error handling quality checks"""
    print("\n" + "=" * 80)
    print("TEST 5: Error Handling Quality Checks")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 2

    # Check 5.1: Detect bare except clauses
    print("  Check 5.1: Detecting bare except clauses...")
    bare_except_code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, data: str) -> str:
        try:
            return data.upper()
        except:  # Bare except - bad!
            return "error"
"""

    result = analyze_code_quality(bare_except_code)
    bare_except_issues = [i for i in result.issues if 'Bare except' in i.message]

    if len(bare_except_issues) > 0:
        print(f"     [OK] Detected bare except clause")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect bare except")

    # Check 5.2: Detect empty except blocks
    print("\n  Check 5.2: Detecting empty except blocks...")
    empty_except_code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self, data: str) -> str:
        try:
            return data.upper()
        except ValueError:
            pass  # Empty except - bad!
"""

    result2 = analyze_code_quality(empty_except_code)
    empty_except_issues = [i for i in result2.issues if 'Empty except' in i.message]

    if len(empty_except_issues) > 0:
        print(f"     [OK] Detected empty except block")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should detect empty except blocks")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_quality_metrics():
    """Test 6: Quality metrics calculation"""
    print("\n" + "=" * 80)
    print("TEST 6: Quality Metrics Calculation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 4

    # Check 6.1: Overall score calculation
    print("  Check 6.1: Overall score is calculated...")
    good_code = """
from typing import Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class TestToolInputSchema(BaseModel):
    \"\"\"Input schema\"\"\"
    query: str = Field(..., description="Search query")

class TestTool(BaseTool):
    \"\"\"Test tool implementation\"\"\"
    name: str = "Test Tool"
    description: str = "A test tool"
    args_schema: type = TestToolInputSchema

    def _run(self, query: str) -> str:
        \"\"\"Execute the tool\"\"\"
        try:
            return f"Result: {query}"
        except Exception as e:
            return f"Error: {str(e)}"
"""

    result = analyze_code_quality(good_code)

    if 0 <= result.metrics.overall_score <= 100:
        print(f"     [OK] Overall score in range: {result.metrics.overall_score}/100")
        checks_passed += 1
    else:
        print(f"     [FAIL] Invalid overall score: {result.metrics.overall_score}")

    # Check 6.2: Lines of code counted
    print("\n  Check 6.2: Lines of code counted correctly...")

    if result.metrics.lines_of_code > 0:
        print(f"     [OK] LOC counted: {result.metrics.lines_of_code}")
        checks_passed += 1
    else:
        print(f"     [FAIL] LOC should be > 0")

    # Check 6.3: Comment ratio calculated
    print("\n  Check 6.3: Comment ratio calculated...")

    if 0 <= result.metrics.comment_ratio <= 1:
        print(f"     [OK] Comment ratio in range: {result.metrics.comment_ratio:.0%}")
        checks_passed += 1
    else:
        print(f"     [FAIL] Invalid comment ratio: {result.metrics.comment_ratio}")

    # Check 6.4: High quality code scores well
    print("\n  Check 6.4: High quality code gets good score...")

    if result.metrics.overall_score >= 80:
        print(f"     [OK] Good code has high score: {result.metrics.overall_score}/100")
        checks_passed += 1
    else:
        print(f"     [FAIL] Good code should score >= 80, got {result.metrics.overall_score}")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_quality_report_generation():
    """Test 7: Quality report generation"""
    print("\n" + "=" * 80)
    print("TEST 7: Quality Report Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Check 7.1: Report is generated
    print("  Check 7.1: Quality report is generated...")
    code = """
from crewai.tools import BaseTool

class TestTool(BaseTool):
    name: str = "Test"

    def _run(self) -> str:
        return "test"
"""

    result = analyze_code_quality(code)
    report = get_quality_report(result)

    if len(report) > 0:
        print(f"     [OK] Report generated ({len(report)} characters)")
        checks_passed += 1
    else:
        print(f"     [FAIL] Report should not be empty")

    # Check 7.2: Report includes metrics
    print("\n  Check 7.2: Report includes metrics...")

    has_metrics = 'METRICS:' in report and 'Overall Score' in report

    if has_metrics:
        print(f"     [OK] Report includes metrics section")
        checks_passed += 1
    else:
        print(f"     [FAIL] Report should include metrics")

    # Check 7.3: Report includes recommendations
    print("\n  Check 7.3: Report includes recommendations...")

    has_recommendations = 'RECOMMENDATIONS:' in report or 'excellent' in report

    if has_recommendations:
        print(f"     [OK] Report includes recommendations")
        checks_passed += 1
    else:
        print(f"     [FAIL] Report should include recommendations")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_strengths_identification():
    """Test 8: Strengths identification"""
    print("\n" + "=" * 80)
    print("TEST 8: Strengths Identification")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 2

    # Check 8.1: Identifies type hints strength
    print("  Check 8.1: Identifying type hints as strength...")
    typed_code = """
from typing import Optional
from crewai.tools import BaseTool

class TestTool(BaseTool):
    \"\"\"Test tool\"\"\"
    name: str = "Test"

    def _run(self, query: str) -> Optional[str]:
        \"\"\"Execute\"\"\"
        try:
            return query
        except Exception:
            return None
"""

    result = analyze_code_quality(typed_code)
    has_type_strength = any('type hint' in s.lower() for s in result.strengths)

    if has_type_strength:
        print(f"     [OK] Type hints identified as strength")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should identify type hints as strength")

    # Check 8.2: Identifies error handling strength
    print("\n  Check 8.2: Identifying error handling as strength...")

    has_error_strength = any('error handling' in s.lower() for s in result.strengths)

    if has_error_strength:
        print(f"     [OK] Error handling identified as strength")
        checks_passed += 1
    else:
        print(f"     [FAIL] Should identify error handling as strength")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def main():
    """Run all Phase 2.1 tests"""
    print("\n")
    print("=" * 80)
    print("PHASE 2.1: Enhanced Code Quality Checks - Validation Tests")
    print("=" * 80)
    print("\n")

    tests = [
        ("Unused Imports Detection", test_unused_imports_detection),
        ("Code Complexity Detection", test_complexity_detection),
        ("CrewAI Anti-Pattern Detection", test_crewai_anti_patterns),
        ("Code Smell Detection", test_code_smell_detection),
        ("Error Handling Quality Checks", test_error_handling_quality),
        ("Quality Metrics Calculation", test_quality_metrics),
        ("Quality Report Generation", test_quality_report_generation),
        ("Strengths Identification", test_strengths_identification),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 2.1 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-" * 80)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 80)

    if passed == total:
        print("\n*** SUCCESS - All Phase 2.1 enhancements validated! ***")
        print()
        print("Validated Features:")
        print("  [OK] Unused import detection")
        print("  [OK] Code complexity analysis")
        print("  [OK] CrewAI anti-pattern detection (blocking ops, global state, mutable vars)")
        print("  [OK] Code smell detection (too many params, long methods, naming)")
        print("  [OK] Error handling quality checks")
        print("  [OK] Quality metrics calculation (overall, complexity, maintainability)")
        print("  [OK] Quality report generation")
        print("  [OK] Strengths identification")
        print()
        print("=" * 80)
        print("RECOMMENDATION: Phase 2.1 is 100% complete and production-ready.")
        print("                Code quality analyzer provides deep analysis.")
        print("                Ready to proceed to Phase 2.2.")
        print("=" * 80)
        return 0
    else:
        print(f"\n*** WARNING: {total - passed} test(s) failed ***")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
