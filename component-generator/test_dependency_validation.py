"""
Test script for dependency validation

This script tests the dependency validation functionality to ensure
it correctly identifies supported/unsupported libraries and provides
appropriate warnings and suggestions.

Usage:
    python test_dependency_validation.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dependency_validator import DependencyValidator, get_validation_summary
from supported_libraries import is_supported, validate_dependencies


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_basic_validation():
    """Test basic is_supported function"""
    print_section("TEST 1: Basic Library Support Checks")

    test_cases = [
        ("requests", True, "Supported external library"),
        ("pandas", True, "Supported external library"),
        ("json", True, "Python stdlib"),
        ("datetime", True, "Python stdlib"),
        ("crewai", True, "Core crewai library"),
        ("unsupported_fake_lib", False, "Unsupported library"),
        ("polars", False, "Unsupported data library"),
    ]

    for lib, expected, description in test_cases:
        result = is_supported(lib)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: {lib} - {description}")
        print(f"   Expected: {expected}, Got: {result}\n")


def test_dependency_list_validation():
    """Test validate_dependencies with lists"""
    print_section("TEST 2: Dependency List Validation")

    test_lists = [
        {
            "name": "All Supported",
            "deps": ["requests", "pandas", "json", "datetime"],
            "expected_all_supported": True
        },
        {
            "name": "Mixed Supported/Unsupported",
            "deps": ["requests", "fake_lib", "pandas", "another_fake"],
            "expected_all_supported": False
        },
        {
            "name": "Only Stdlib",
            "deps": ["json", "datetime", "os", "sys"],
            "expected_all_supported": True
        },
        {
            "name": "Empty List",
            "deps": [],
            "expected_all_supported": True
        }
    ]

    for test_case in test_lists:
        print(f"\n📋 Test Case: {test_case['name']}")
        print(f"Dependencies: {test_case['deps']}")

        result = validate_dependencies(test_case['deps'])

        print(f"\nResults:")
        print(f"  All Supported: {result['all_supported']}")
        print(f"  Supported: {result['supported']}")
        print(f"  Unsupported: {result['unsupported']}")
        print(f"  Stdlib: {result['stdlib']}")
        print(f"  External: {result['external']}")

        if result['alternatives']:
            print(f"\n  Alternatives:")
            for dep, alts in result['alternatives'].items():
                print(f"    {dep} → {', '.join(alts)}")

        status = "✅ PASS" if result['all_supported'] == test_case['expected_all_supported'] else "❌ FAIL"
        print(f"\n{status}: Expected all_supported={test_case['expected_all_supported']}, Got={result['all_supported']}")


def test_dependency_validator_class():
    """Test DependencyValidator class with detailed validation"""
    print_section("TEST 3: DependencyValidator Class")

    validator = DependencyValidator()

    # Test Case 1: All supported dependencies
    print("\n📦 Test 3.1: All Supported Dependencies")
    deps1 = ["requests", "pandas", "json", "datetime"]
    result1 = validator.validate(deps1)
    print(get_validation_summary(result1))

    assert result1.all_supported == True, "Expected all_supported=True"
    assert len(result1.unsupported) == 0, "Expected no unsupported dependencies"
    assert result1.can_proceed == True, "Expected can_proceed=True"
    print("✅ Test 3.1 PASSED")

    # Test Case 2: Mixed dependencies
    print("\n📦 Test 3.2: Mixed Supported/Unsupported Dependencies")
    deps2 = ["requests", "fake_lib", "pandas", "another_fake"]
    result2 = validator.validate(deps2)
    print(get_validation_summary(result2))

    assert result2.all_supported == False, "Expected all_supported=False"
    assert len(result2.unsupported) == 2, "Expected 2 unsupported dependencies"
    assert result2.manual_implementation_needed == True, "Expected manual implementation needed"
    assert len(result2.warnings) > 0, "Expected warnings"
    assert len(result2.suggestions) > 0, "Expected suggestions"
    print("✅ Test 3.2 PASSED")

    # Test Case 3: Only unsupported dependencies
    print("\n📦 Test 3.3: Only Unsupported Dependencies")
    deps3 = ["fake_lib1", "fake_lib2", "fake_lib3"]
    result3 = validator.validate(deps3)
    print(get_validation_summary(result3))

    assert result3.all_supported == False, "Expected all_supported=False"
    assert len(result3.unsupported) == 3, "Expected 3 unsupported dependencies"
    assert len(result3.supported) == 0, "Expected no supported dependencies"
    print("✅ Test 3.3 PASSED")

    # Test Case 4: Empty dependencies
    print("\n📦 Test 3.4: Empty Dependencies List")
    deps4 = []
    result4 = validator.validate(deps4)
    print(get_validation_summary(result4))

    assert result4.all_supported == True, "Expected all_supported=True for empty list"
    assert len(result4.unsupported) == 0, "Expected no unsupported dependencies"
    print("✅ Test 3.4 PASSED")


def test_manual_implementation_guide():
    """Test manual implementation guide generation"""
    print_section("TEST 4: Manual Implementation Guide")

    validator = DependencyValidator()

    test_libs = [
        "requests",  # Should match http_client pattern
        "ujson",     # Should match json_processing pattern
        "fake_lib",  # Should get default guide
    ]

    for lib in test_libs:
        print(f"\n🔧 Manual Implementation Guide for '{lib}':")
        guide = validator.get_manual_implementation_guide(lib)

        print(f"  Pattern: {guide['pattern']}")
        print(f"  Description: {guide['description']}")
        print(f"  Recommended Stdlib: {', '.join(guide['recommended_stdlib'])}")
        print(f"  Approach: {guide['implementation_approach'][:100]}...")


def test_requirements_generation():
    """Test requirements.txt generation"""
    print_section("TEST 5: Requirements.txt Generation")

    validator = DependencyValidator()

    deps = ["requests", "pandas", "fake_lib", "json", "crewai"]
    print(f"Input dependencies: {deps}\n")

    requirements = validator.generate_requirements_txt(deps)
    print("Generated requirements.txt:")
    print("-" * 60)
    print(requirements)
    print("-" * 60)


def test_code_import_extraction():
    """Test extracting and validating imports from code"""
    print_section("TEST 6: Code Import Extraction & Validation")

    validator = DependencyValidator()

    sample_code = """
import json
import requests
from pandas import DataFrame
from fake_lib import something
import datetime
from another_fake import FakeClass
"""

    print("Sample code:")
    print(sample_code)
    print("\nValidation results:")

    result = validator.validate_imports_in_code(sample_code)
    print(get_validation_summary(result))


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  DEPENDENCY VALIDATION TEST SUITE")
    print("  Phase 1.5: Testing Dependency Validation")
    print("=" * 80)

    try:
        test_basic_validation()
        test_dependency_list_validation()
        test_dependency_validator_class()
        test_manual_implementation_guide()
        test_requirements_generation()
        test_code_import_extraction()

        print("\n" + "=" * 80)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"  ❌ TEST FAILED: {str(e)}")
        print("=" * 80 + "\n")
        raise

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"  ❌ ERROR: {str(e)}")
        print("=" * 80 + "\n")
        raise


if __name__ == "__main__":
    run_all_tests()
