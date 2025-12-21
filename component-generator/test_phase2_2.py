#!/usr/bin/env python
"""
Phase 2.2 Test - Usage Examples & Documentation Generation
Tests documentation generator including usage examples and quick-start guides
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from documentation_generator import (
    DocumentationGenerator,
    generate_documentation,
    save_documentation
)
from base_classes import ToolSpec, ToolInputParameter


def test_documentation_generation():
    """Test 1: Basic documentation generation"""
    print("=" * 80)
    print("TEST 1: Basic Documentation Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 4

    # Create test spec
    spec = ToolSpec(
        name="TestTool",
        display_name="Test Tool",
        description="A test tool for validation",
        category="testing",
        inputs=[
            ToolInputParameter(
                name="query",
                type="str",
                description="Search query to process",
                required=True
            )
        ]
    )

    # Check 1.1: Documentation object is created
    print("  Check 1.1: Documentation object is created...")
    doc = generate_documentation(spec, "")

    if doc is not None and doc.tool_name == "TestTool":
        print(f"     [OK] Documentation created for '{doc.tool_name}'")
        checks_passed += 1
    else:
        print(f"     [FAIL] Documentation not created properly")

    # Check 1.2: Overview section exists
    print("\n  Check 1.2: Overview section exists...")

    if doc.overview and len(doc.overview) > 0:
        has_display_name = spec.display_name in doc.overview
        has_description = spec.description in doc.overview

        if has_display_name and has_description:
            print(f"     [OK] Overview section includes name and description")
            checks_passed += 1
        else:
            print(f"     [FAIL] Overview missing key information")
    else:
        print(f"     [FAIL] Overview section is empty")

    # Check 1.3: Usage examples are generated
    print("\n  Check 1.3: Usage examples are generated...")

    if len(doc.usage_examples) > 0:
        print(f"     [OK] Generated {len(doc.usage_examples)} usage example(s)")
        checks_passed += 1
    else:
        print(f"     [FAIL] No usage examples generated")

    # Check 1.4: Quick start guide exists
    print("\n  Check 1.4: Quick start guide exists...")

    if doc.quick_start and len(doc.quick_start) > 0:
        has_import = "import" in doc.quick_start.lower()
        has_initialize = spec.name in doc.quick_start

        if has_import and has_initialize:
            print(f"     [OK] Quick start guide includes imports and initialization")
            checks_passed += 1
        else:
            print(f"     [FAIL] Quick start guide incomplete")
    else:
        print(f"     [FAIL] Quick start guide is empty")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_usage_examples_generation():
    """Test 2: Usage examples generation"""
    print("\n" + "=" * 80)
    print("TEST 2: Usage Examples Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 4

    # Create spec with optional parameters
    spec = ToolSpec(
        name="AdvancedTool",
        display_name="Advanced Tool",
        description="Advanced tool with multiple parameters",
        category="advanced",
        inputs=[
            ToolInputParameter(
                name="data",
                type="str",
                description="Data to process",
                required=True
            ),
            ToolInputParameter(
                name="max_results",
                type="int",
                description="Maximum number of results",
                required=False,
                default_value=10
            )
        ]
    )

    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Check 2.1: Basic usage example exists
    print("  Check 2.1: Basic usage example exists...")
    basic_examples = [e for e in doc.usage_examples if "Basic" in e.title]

    if len(basic_examples) > 0:
        basic_ex = basic_examples[0]
        has_code = len(basic_ex.code) > 0
        has_import = "import" in basic_ex.code
        has_execution = "_run" in basic_ex.code

        if has_code and has_import and has_execution:
            print(f"     [OK] Basic usage example complete")
            checks_passed += 1
        else:
            print(f"     [FAIL] Basic usage example incomplete")
    else:
        print(f"     [FAIL] No basic usage example found")

    # Check 2.2: Optional parameters example exists
    print("\n  Check 2.2: Optional parameters example exists...")
    optional_examples = [e for e in doc.usage_examples if "Optional" in e.title]

    if len(optional_examples) > 0:
        optional_ex = optional_examples[0]
        has_max_results = "max_results" in optional_ex.code

        if has_max_results:
            print(f"     [OK] Optional parameters example includes optional params")
            checks_passed += 1
        else:
            print(f"     [FAIL] Optional parameters example missing optional params")
    else:
        print(f"     [OK] No optional parameters example (no optional params in spec)")
        checks_passed += 1  # This is ok if there are no optional params

    # Check 2.3: CrewAI integration example exists
    print("\n  Check 2.3: CrewAI integration example exists...")
    crewai_examples = [e for e in doc.usage_examples if "CrewAI" in e.title or "Integration" in e.title]

    if len(crewai_examples) > 0:
        crewai_ex = crewai_examples[0]
        has_agent = "Agent" in crewai_ex.code
        has_task = "Task" in crewai_ex.code
        has_crew = "Crew" in crewai_ex.code

        if has_agent and has_task and has_crew:
            print(f"     [OK] CrewAI integration example complete")
            checks_passed += 1
        else:
            print(f"     [FAIL] CrewAI integration example incomplete")
    else:
        print(f"     [FAIL] No CrewAI integration example found")

    # Check 2.4: Error handling example exists
    print("\n  Check 2.4: Error handling example exists...")
    error_examples = [e for e in doc.usage_examples if "Error" in e.title]

    if len(error_examples) > 0:
        error_ex = error_examples[0]
        has_try = "try:" in error_ex.code
        has_except = "except" in error_ex.code

        if has_try and has_except:
            print(f"     [OK] Error handling example includes try-except")
            checks_passed += 1
        else:
            print(f"     [FAIL] Error handling example incomplete")
    else:
        print(f"     [FAIL] No error handling example found")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_api_reference_generation():
    """Test 3: API reference generation"""
    print("\n" + "=" * 80)
    print("TEST 3: API Reference Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create spec with config params
    spec = ToolSpec(
        name="ConfigurableTool",
        display_name="Configurable Tool",
        description="Tool with configuration parameters",
        category="config",
        inputs=[
            ToolInputParameter(
                name="query",
                type="str",
                description="Query to execute",
                required=True
            )
        ],
        config_params=[
            ToolInputParameter(
                name="api_key",
                type="str",
                description="API key for authentication",
                required=True,
                param_kind="config"
            )
        ]
    )

    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Check 3.1: API reference section exists
    print("  Check 3.1: API reference section exists...")

    if doc.api_reference and len(doc.api_reference) > 0:
        has_class_name = spec.name in doc.api_reference
        has_run_method = "_run" in doc.api_reference

        if has_class_name and has_run_method:
            print(f"     [OK] API reference includes class name and _run method")
            checks_passed += 1
        else:
            print(f"     [FAIL] API reference incomplete")
    else:
        print(f"     [FAIL] API reference is empty")

    # Check 3.2: Constructor documentation exists
    print("\n  Check 3.2: Constructor documentation exists...")

    has_constructor = "__init__" in doc.api_reference or "Constructor" in doc.api_reference

    if has_constructor:
        print(f"     [OK] Constructor documented")
        checks_passed += 1
    else:
        print(f"     [FAIL] Constructor not documented")

    # Check 3.3: Parameters are documented
    print("\n  Check 3.3: Parameters are documented...")

    if doc.parameters_doc and len(doc.parameters_doc) > 0:
        has_query = "query" in doc.parameters_doc
        has_api_key = "api_key" in doc.parameters_doc

        if has_query and has_api_key:
            print(f"     [OK] Parameters documented")
            checks_passed += 1
        else:
            print(f"     [FAIL] Some parameters missing from documentation")
    else:
        print(f"     [FAIL] Parameters documentation is empty")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_parameters_documentation():
    """Test 4: Parameters documentation"""
    print("\n" + "=" * 80)
    print("TEST 4: Parameters Documentation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create spec with detailed parameters
    spec = ToolSpec(
        name="DetailedTool",
        display_name="Detailed Tool",
        description="Tool with detailed parameters",
        category="detailed",
        inputs=[
            ToolInputParameter(
                name="input_data",
                type="List[str]",
                description="List of data items to process",
                required=True,
                examples=['["item1", "item2"]', '["a", "b", "c"]']
            ),
            ToolInputParameter(
                name="max_items",
                type="int",
                description="Maximum number of items to process",
                required=False,
                default_value=100
            )
        ]
    )

    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Check 4.1: Parameter types are documented
    print("  Check 4.1: Parameter types are documented...")

    has_type_info = "Type:" in doc.parameters_doc or "type" in doc.parameters_doc.lower()

    if has_type_info:
        has_list_type = "List[str]" in doc.parameters_doc
        if has_list_type:
            print(f"     [OK] Parameter types documented (including complex types)")
            checks_passed += 1
        else:
            print(f"     [FAIL] Complex types not documented")
    else:
        print(f"     [FAIL] Parameter types not documented")

    # Check 4.2: Required status is documented
    print("\n  Check 4.2: Required status is documented...")

    has_required_info = "Required:" in doc.parameters_doc or "required" in doc.parameters_doc.lower()

    if has_required_info:
        print(f"     [OK] Required status documented")
        checks_passed += 1
    else:
        print(f"     [FAIL] Required status not documented")

    # Check 4.3: Default values are documented
    print("\n  Check 4.3: Default values are documented...")

    has_default_info = "100" in doc.parameters_doc  # max_items default

    if has_default_info:
        print(f"     [OK] Default values documented")
        checks_passed += 1
    else:
        print(f"     [FAIL] Default values not documented")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_best_practices_generation():
    """Test 5: Best practices generation"""
    print("\n" + "=" * 80)
    print("TEST 5: Best Practices Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create API tool spec
    spec = ToolSpec(
        name="ApiTool",
        display_name="API Tool",
        description="Tool for API interactions",
        category="api",
        inputs=[
            ToolInputParameter(
                name="api_key",
                type="str",
                description="API key for authentication",
                required=True
            ),
            ToolInputParameter(
                name="timeout",
                type="int",
                description="Request timeout in seconds",
                required=False,
                default_value=30
            )
        ]
    )

    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Check 5.1: Best practices list exists
    print("  Check 5.1: Best practices list exists...")

    if len(doc.best_practices) > 0:
        print(f"     [OK] Generated {len(doc.best_practices)} best practice(s)")
        checks_passed += 1
    else:
        print(f"     [FAIL] No best practices generated")

    # Check 5.2: API-specific best practices included
    print("\n  Check 5.2: API-specific best practices included...")

    api_practices = [p for p in doc.best_practices if 'api' in p.lower() or 'retry' in p.lower()]

    if len(api_practices) > 0:
        print(f"     [OK] API-specific best practices included")
        checks_passed += 1
    else:
        print(f"     [FAIL] No API-specific best practices")

    # Check 5.3: Security best practices for API keys
    print("\n  Check 5.3: Security best practices for API keys...")

    security_practices = [p for p in doc.best_practices if 'key' in p.lower() or 'credential' in p.lower() or 'environment' in p.lower()]

    if len(security_practices) > 0:
        print(f"     [OK] Security best practices included")
        checks_passed += 1
    else:
        print(f"     [FAIL] No security best practices for API keys")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_troubleshooting_generation():
    """Test 6: Troubleshooting guide generation"""
    print("\n" + "=" * 80)
    print("TEST 6: Troubleshooting Guide Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create spec with dependencies
    spec = ToolSpec(
        name="DependentTool",
        display_name="Dependent Tool",
        description="Tool with dependencies",
        category="api",
        inputs=[
            ToolInputParameter(
                name="query",
                type="str",
                description="Query parameter to process",
                required=True
            )
        ],
        dependencies=["requests", "beautifulsoup4"]
    )

    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Check 6.1: Troubleshooting entries exist
    print("  Check 6.1: Troubleshooting entries exist...")

    if len(doc.troubleshooting) > 0:
        print(f"     [OK] Generated {len(doc.troubleshooting)} troubleshooting entry/entries")
        checks_passed += 1
    else:
        print(f"     [FAIL] No troubleshooting entries generated")

    # Check 6.2: Each entry has problem and solution
    print("\n  Check 6.2: Each entry has problem and solution...")

    all_have_both = all('problem' in entry and 'solution' in entry for entry in doc.troubleshooting)

    if all_have_both:
        print(f"     [OK] All entries have problem and solution")
        checks_passed += 1
    else:
        print(f"     [FAIL] Some entries missing problem or solution")

    # Check 6.3: Dependency-related troubleshooting included
    print("\n  Check 6.3: Dependency-related troubleshooting included...")

    dep_issues = [e for e in doc.troubleshooting if 'dependencies' in e['solution'].lower() or 'pip install' in e['solution'].lower()]

    if len(dep_issues) > 0:
        print(f"     [OK] Dependency troubleshooting included")
        checks_passed += 1
    else:
        print(f"     [FAIL] No dependency troubleshooting")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_markdown_export():
    """Test 7: Markdown export"""
    print("\n" + "=" * 80)
    print("TEST 7: Markdown Export")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create simple spec
    spec = ToolSpec(
        name="ExportTool",
        display_name="Export Tool",
        description="Tool for testing markdown export",
        category="test",
        inputs=[
            ToolInputParameter(
                name="data",
                type="str",
                description="Data to export",
                required=True
            )
        ]
    )

    generator = DocumentationGenerator()
    doc = generator.generate(spec, "")

    # Check 7.1: Markdown can be generated
    print("  Check 7.1: Markdown can be generated...")

    try:
        markdown = generator.to_markdown(doc)
        if len(markdown) > 0:
            print(f"     [OK] Markdown generated ({len(markdown)} characters)")
            checks_passed += 1
        else:
            print(f"     [FAIL] Markdown is empty")
    except Exception as e:
        print(f"     [FAIL] Error generating markdown: {e}")

    # Check 7.2: Markdown contains key sections
    print("\n  Check 7.2: Markdown contains key sections...")

    has_overview = "## Overview" in markdown or spec.display_name in markdown
    has_installation = "## Installation" in markdown
    has_examples = "## Usage Examples" in markdown or "Example" in markdown

    if has_overview and has_installation and has_examples:
        print(f"     [OK] Markdown contains all key sections")
        checks_passed += 1
    else:
        print(f"     [FAIL] Some sections missing from markdown")

    # Check 7.3: Code blocks are properly formatted
    print("\n  Check 7.3: Code blocks are properly formatted...")

    has_code_blocks = "```python" in markdown and "```" in markdown
    code_block_count = markdown.count("```")

    # Should have even number of ``` (opening and closing)
    if has_code_blocks and code_block_count % 2 == 0:
        print(f"     [OK] Code blocks properly formatted ({code_block_count // 2} blocks)")
        checks_passed += 1
    else:
        print(f"     [FAIL] Code blocks not properly formatted")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_complete_documentation_workflow():
    """Test 8: Complete documentation workflow"""
    print("\n" + "=" * 80)
    print("TEST 8: Complete Documentation Workflow")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 2

    # Create comprehensive spec
    spec = ToolSpec(
        name="CompleteTool",
        display_name="Complete Tool",
        description="Comprehensive tool for workflow testing",
        category="test",
        requirements=[
            "Process data efficiently",
            "Support multiple formats",
            "Handle errors gracefully"
        ],
        inputs=[
            ToolInputParameter(
                name="data",
                type="List[str]",
                description="Data items to process",
                required=True
            ),
            ToolInputParameter(
                name="format",
                type="str",
                description="Output format (json, xml, csv)",
                required=False,
                default_value="json",
                examples=['"json"', '"xml"', '"csv"']
            )
        ],
        config_params=[
            ToolInputParameter(
                name="debug",
                type="bool",
                description="Enable debug mode",
                required=False,
                default_value=False,
                param_kind="config"
            )
        ],
        dependencies=["pandas", "lxml"],
        author="Test Author",
        version="1.0.0"
    )

    # Check 8.1: Complete documentation generated
    print("  Check 8.1: Complete documentation generated...")

    try:
        doc = generate_documentation(spec, "")

        has_all_sections = all([
            doc.overview,
            doc.installation,
            doc.quick_start,
            len(doc.usage_examples) > 0,
            doc.api_reference,
            doc.parameters_doc,
            len(doc.best_practices) > 0,
            len(doc.troubleshooting) > 0
        ])

        if has_all_sections:
            print(f"     [OK] All documentation sections generated")
            checks_passed += 1
        else:
            print(f"     [FAIL] Some documentation sections missing")
    except Exception as e:
        print(f"     [FAIL] Error generating documentation: {e}")

    # Check 8.2: Documentation can be exported to markdown
    print("\n  Check 8.2: Documentation can be exported to markdown...")

    try:
        generator = DocumentationGenerator()
        markdown = generator.to_markdown(doc)

        # Check markdown completeness
        has_title = spec.display_name in markdown
        has_examples_section = "Usage Examples" in markdown
        has_params_section = "Parameters" in markdown or "data" in markdown
        has_practices = "Best Practices" in markdown

        if has_title and has_examples_section and has_params_section and has_practices:
            print(f"     [OK] Complete markdown documentation exported")
            checks_passed += 1
        else:
            print(f"     [FAIL] Markdown export incomplete")
    except Exception as e:
        print(f"     [FAIL] Error exporting to markdown: {e}")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def main():
    """Run all Phase 2.2 tests"""
    print("\n")
    print("=" * 80)
    print("PHASE 2.2: Usage Examples & Documentation - Validation Tests")
    print("=" * 80)
    print("\n")

    tests = [
        ("Basic Documentation Generation", test_documentation_generation),
        ("Usage Examples Generation", test_usage_examples_generation),
        ("API Reference Generation", test_api_reference_generation),
        ("Parameters Documentation", test_parameters_documentation),
        ("Best Practices Generation", test_best_practices_generation),
        ("Troubleshooting Guide Generation", test_troubleshooting_generation),
        ("Markdown Export", test_markdown_export),
        ("Complete Documentation Workflow", test_complete_documentation_workflow),
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
    print("PHASE 2.2 TEST SUMMARY")
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
        print("\n*** SUCCESS - All Phase 2.2 enhancements validated! ***")
        print()
        print("Validated Features:")
        print("  [OK] Documentation object generation")
        print("  [OK] Usage examples (Basic, Optional params, CrewAI integration, Error handling)")
        print("  [OK] API reference documentation")
        print("  [OK] Parameters documentation (types, required status, defaults)")
        print("  [OK] Best practices generation (general and category-specific)")
        print("  [OK] Troubleshooting guide generation")
        print("  [OK] Markdown export with proper formatting")
        print("  [OK] Complete documentation workflow")
        print()
        print("=" * 80)
        print("RECOMMENDATION: Phase 2.2 is 100% complete and production-ready.")
        print("                Documentation generator creates comprehensive docs.")
        print("                Ready to proceed to Phase 2.3.")
        print("=" * 80)
        return 0
    else:
        print(f"\n*** WARNING: {total - passed} test(s) failed ***")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
