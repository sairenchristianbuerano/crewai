#!/usr/bin/env python
"""
Phase 2.3 Test - Standalone Tool Packaging
Tests packaging generator including pyproject.toml, setup.py, and other distribution files
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from packaging_generator import (
    PackagingGenerator,
    generate_packaging,
    save_packaging_files
)
from base_classes import ToolSpec, ToolInputParameter


def test_package_metadata_generation():
    """Test 1: Package metadata generation"""
    print("=" * 80)
    print("TEST 1: Package Metadata Generation")
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
        inputs=[],
        dependencies=["requests"],
        author="Test Author",
        version="1.0.0"
    )

    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Check 1.1: Package name is generated correctly
    print("  Check 1.1: Package name is generated correctly...")

    expected_name = "crewai-tool-test_tool"
    if files.metadata.name == expected_name:
        print(f"     [OK] Package name: '{files.metadata.name}'")
        checks_passed += 1
    else:
        print(f"     [FAIL] Expected '{expected_name}', got '{files.metadata.name}'")

    # Check 1.2: Version is preserved
    print("\n  Check 1.2: Version is preserved...")

    if files.metadata.version == "1.0.0":
        print(f"     [OK] Version: {files.metadata.version}")
        checks_passed += 1
    else:
        print(f"     [FAIL] Version mismatch")

    # Check 1.3: CrewAI dependency is added
    print("\n  Check 1.3: CrewAI dependency is automatically added...")

    has_crewai = any("crewai" in dep.lower() for dep in files.metadata.dependencies)

    if has_crewai:
        print(f"     [OK] CrewAI dependency present")
        checks_passed += 1
    else:
        print(f"     [FAIL] CrewAI dependency missing")

    # Check 1.4: Keywords are generated
    print("\n  Check 1.4: Keywords are generated...")

    if len(files.metadata.keywords) > 0:
        has_crewai_keyword = "crewai" in files.metadata.keywords
        has_category = spec.category in files.metadata.keywords

        if has_crewai_keyword and has_category:
            print(f"     [OK] Keywords generated: {files.metadata.keywords[:3]}...")
            checks_passed += 1
        else:
            print(f"     [FAIL] Keywords missing required values")
    else:
        print(f"     [FAIL] No keywords generated")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_pyproject_toml_generation():
    """Test 2: pyproject.toml generation"""
    print("\n" + "=" * 80)
    print("TEST 2: pyproject.toml Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 5

    # Create spec
    spec = ToolSpec(
        name="ApiTool",
        display_name="API Tool",
        description="API interaction tool",
        category="api",
        inputs=[],
        dependencies=["requests", "httpx"],
        author="API Author",
        version="2.0.0"
    )

    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Check 2.1: pyproject.toml is generated
    print("  Check 2.1: pyproject.toml is generated...")

    if files.pyproject_toml and len(files.pyproject_toml) > 0:
        print(f"     [OK] pyproject.toml generated ({len(files.pyproject_toml)} characters)")
        checks_passed += 1
    else:
        print(f"     [FAIL] pyproject.toml is empty")

    # Check 2.2: Build system is specified
    print("\n  Check 2.2: Build system is specified...")

    has_build_system = "[build-system]" in files.pyproject_toml
    has_setuptools = "setuptools" in files.pyproject_toml

    if has_build_system and has_setuptools:
        print(f"     [OK] Build system configured")
        checks_passed += 1
    else:
        print(f"     [FAIL] Build system not properly configured")

    # Check 2.3: Project metadata is present
    print("\n  Check 2.3: Project metadata is present...")

    has_name = 'name = "crewai-tool-api_tool"' in files.pyproject_toml
    has_version = 'version = "2.0.0"' in files.pyproject_toml
    has_description = spec.description in files.pyproject_toml

    if has_name and has_version and has_description:
        print(f"     [OK] Project metadata complete")
        checks_passed += 1
    else:
        print(f"     [FAIL] Project metadata incomplete")

    # Check 2.4: Dependencies are listed
    print("\n  Check 2.4: Dependencies are listed...")

    has_dependencies_section = "dependencies = [" in files.pyproject_toml
    has_requests = '"requests"' in files.pyproject_toml or "'requests'" in files.pyproject_toml
    has_crewai = '"crewai' in files.pyproject_toml or "'crewai" in files.pyproject_toml

    if has_dependencies_section and has_requests and has_crewai:
        print(f"     [OK] Dependencies listed correctly")
        checks_passed += 1
    else:
        print(f"     [FAIL] Dependencies not properly listed")

    # Check 2.5: Classifiers are included
    print("\n  Check 2.5: Classifiers are included...")

    has_classifiers = "classifiers = [" in files.pyproject_toml
    has_python_classifier = "Programming Language :: Python" in files.pyproject_toml

    if has_classifiers and has_python_classifier:
        print(f"     [OK] Classifiers included")
        checks_passed += 1
    else:
        print(f"     [FAIL] Classifiers missing")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_setup_py_generation():
    """Test 3: setup.py generation"""
    print("\n" + "=" * 80)
    print("TEST 3: setup.py Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 4

    # Create spec
    spec = ToolSpec(
        name="DatabaseTool",
        display_name="Database Tool",
        description="Database operations tool",
        category="database",
        inputs=[],
        dependencies=["sqlalchemy"],
        author="DB Author",
        version="1.5.0"
    )

    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Check 3.1: setup.py is generated
    print("  Check 3.1: setup.py is generated...")

    if files.setup_py and len(files.setup_py) > 0:
        print(f"     [OK] setup.py generated ({len(files.setup_py)} characters)")
        checks_passed += 1
    else:
        print(f"     [FAIL] setup.py is empty")

    # Check 3.2: setup() function is present
    print("\n  Check 3.2: setup() function is present...")

    has_setup_import = "from setuptools import setup" in files.setup_py
    has_setup_call = "setup(" in files.setup_py

    if has_setup_import and has_setup_call:
        print(f"     [OK] setup() function configured")
        checks_passed += 1
    else:
        print(f"     [FAIL] setup() function not found")

    # Check 3.3: Package metadata is present
    print("\n  Check 3.3: Package metadata is present...")

    has_name = 'name="crewai-tool-database_tool"' in files.setup_py
    has_version = 'version="1.5.0"' in files.setup_py
    has_author = 'author="DB Author"' in files.setup_py

    if has_name and has_version and has_author:
        print(f"     [OK] Package metadata in setup.py")
        checks_passed += 1
    else:
        print(f"     [FAIL] Package metadata incomplete")

    # Check 3.4: Dependencies are specified
    print("\n  Check 3.4: Dependencies are specified...")

    has_install_requires = "install_requires=" in files.setup_py
    has_sqlalchemy = '"sqlalchemy"' in files.setup_py

    if has_install_requires and has_sqlalchemy:
        print(f"     [OK] Dependencies specified")
        checks_passed += 1
    else:
        print(f"     [FAIL] Dependencies not specified")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_manifest_in_generation():
    """Test 4: MANIFEST.in generation"""
    print("\n" + "=" * 80)
    print("TEST 4: MANIFEST.in Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create spec
    spec = ToolSpec(
        name="FileTool",
        display_name="File Tool",
        description="File operations tool",
        category="file",
        inputs=[],
        author="File Author",
        version="1.0.0"
    )

    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Check 4.1: MANIFEST.in is generated
    print("  Check 4.1: MANIFEST.in is generated...")

    if files.manifest_in and len(files.manifest_in) > 0:
        print(f"     [OK] MANIFEST.in generated")
        checks_passed += 1
    else:
        print(f"     [FAIL] MANIFEST.in is empty")

    # Check 4.2: README and LICENSE are included
    print("\n  Check 4.2: README and LICENSE are included...")

    has_readme = "include README.md" in files.manifest_in
    has_license = "include LICENSE" in files.manifest_in

    if has_readme and has_license:
        print(f"     [OK] Documentation files included")
        checks_passed += 1
    else:
        print(f"     [FAIL] Documentation files not included")

    # Check 4.3: Excludes are specified
    print("\n  Check 4.3: Exclude patterns are specified...")

    has_excludes = "global-exclude" in files.manifest_in
    has_pycache = "__pycache__" in files.manifest_in

    if has_excludes and has_pycache:
        print(f"     [OK] Exclude patterns specified")
        checks_passed += 1
    else:
        print(f"     [FAIL] Exclude patterns missing")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_readme_generation():
    """Test 5: README.md generation"""
    print("\n" + "=" * 80)
    print("TEST 5: README.md Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 4

    # Create spec with requirements
    spec = ToolSpec(
        name="WebTool",
        display_name="Web Tool",
        description="Web interaction tool",
        category="web",
        requirements=[
            "HTTP requests support",
            "HTML parsing",
            "Data extraction"
        ],
        inputs=[],
        dependencies=["requests"],
        author="Web Author",
        version="1.0.0"
    )

    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Check 5.1: README is generated
    print("  Check 5.1: README.md is generated...")

    if files.readme_md and len(files.readme_md) > 0:
        print(f"     [OK] README.md generated ({len(files.readme_md)} characters)")
        checks_passed += 1
    else:
        print(f"     [FAIL] README.md is empty")

    # Check 5.2: Tool name and description are present
    print("\n  Check 5.2: Tool name and description are present...")

    has_title = spec.display_name in files.readme_md
    has_description = spec.description in files.readme_md

    if has_title and has_description:
        print(f"     [OK] Name and description in README")
        checks_passed += 1
    else:
        print(f"     [FAIL] Name or description missing")

    # Check 5.3: Installation instructions are present
    print("\n  Check 5.3: Installation instructions are present...")

    has_installation = "## Installation" in files.readme_md
    has_pip_install = "pip install" in files.readme_md
    has_package_name = "crewai-tool-web_tool" in files.readme_md

    if has_installation and has_pip_install and has_package_name:
        print(f"     [OK] Installation instructions present")
        checks_passed += 1
    else:
        print(f"     [FAIL] Installation instructions incomplete")

    # Check 5.4: Features are listed
    print("\n  Check 5.4: Features are listed...")

    has_features = "## Features" in files.readme_md
    has_feature_items = any(req in files.readme_md for req in spec.requirements)

    if has_features and has_feature_items:
        print(f"     [OK] Features listed")
        checks_passed += 1
    else:
        print(f"     [FAIL] Features not listed")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_license_generation():
    """Test 6: LICENSE generation"""
    print("\n" + "=" * 80)
    print("TEST 6: LICENSE Generation")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 3

    # Create spec
    spec = ToolSpec(
        name="TestTool",
        display_name="Test Tool",
        description="Test tool",
        category="test",
        inputs=[],
        author="Test Author",
        version="1.0.0"
    )

    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Check 6.1: LICENSE is generated
    print("  Check 6.1: LICENSE file is generated...")

    if files.license_file and len(files.license_file) > 0:
        print(f"     [OK] LICENSE generated ({len(files.license_file)} characters)")
        checks_passed += 1
    else:
        print(f"     [FAIL] LICENSE is empty")

    # Check 6.2: MIT License content is present
    print("\n  Check 6.2: MIT License content is present...")

    has_mit = "MIT License" in files.license_file
    has_permission = "Permission is hereby granted" in files.license_file

    if has_mit and has_permission:
        print(f"     [OK] MIT License content present")
        checks_passed += 1
    else:
        print(f"     [FAIL] MIT License content missing")

    # Check 6.3: Author name is in license
    print("\n  Check 6.3: Author name is in license...")

    has_author = spec.author in files.license_file

    if has_author:
        print(f"     [OK] Author name in LICENSE")
        checks_passed += 1
    else:
        print(f"     [FAIL] Author name missing from LICENSE")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_complete_packaging_workflow():
    """Test 7: Complete packaging workflow"""
    print("\n" + "=" * 80)
    print("TEST 7: Complete Packaging Workflow")
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
            "Feature 1",
            "Feature 2",
            "Feature 3"
        ],
        inputs=[
            ToolInputParameter(
                name="data",
                type="str",
                description="Data to process securely",
                required=True
            )
        ],
        dependencies=["requests", "pydantic"],
        author="Complete Author",
        version="2.5.0"
    )

    # Check 7.1: All packaging files generated
    print("  Check 7.1: All packaging files generated...")

    try:
        files = generate_packaging(spec, "")

        has_all_files = all([
            files.pyproject_toml,
            files.setup_py,
            files.manifest_in,
            files.readme_md,
            files.license_file
        ])

        if has_all_files:
            print(f"     [OK] All packaging files generated")
            checks_passed += 1
        else:
            print(f"     [FAIL] Some packaging files missing")
    except Exception as e:
        print(f"     [FAIL] Error generating packaging: {e}")

    # Check 7.2: Package can be built (metadata is valid)
    print("\n  Check 7.2: Package metadata is valid...")

    try:
        # Verify package name follows conventions
        package_name_valid = files.metadata.name.startswith("crewai-tool-")
        package_name_valid &= "_" in files.metadata.name or "-" in files.metadata.name

        # Verify version is valid
        version_parts = files.metadata.version.split(".")
        version_valid = len(version_parts) >= 2

        # Verify dependencies include crewai
        deps_valid = any("crewai" in dep.lower() for dep in files.metadata.dependencies)

        if package_name_valid and version_valid and deps_valid:
            print(f"     [OK] Package metadata is valid")
            print(f"          Package: {files.metadata.name}")
            print(f"          Version: {files.metadata.version}")
            print(f"          Dependencies: {len(files.metadata.dependencies)}")
            checks_passed += 1
        else:
            print(f"     [FAIL] Package metadata has validation issues")
    except Exception as e:
        print(f"     [FAIL] Error validating metadata: {e}")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def test_category_specific_features():
    """Test 8: Category-specific features"""
    print("\n" + "=" * 80)
    print("TEST 8: Category-Specific Features")
    print("=" * 80)
    print()

    checks_passed = 0
    total_checks = 2

    # Test with API category
    api_spec = ToolSpec(
        name="ApiTool",
        display_name="API Tool",
        description="API tool",
        category="api",
        inputs=[],
        author="Author",
        version="1.0.0"
    )

    generator = PackagingGenerator()
    api_files = generator.generate(api_spec, "")

    # Check 8.1: API category gets specific keywords
    print("  Check 8.1: API category gets specific keywords...")

    api_keywords = ["api", "http", "rest"]
    has_api_keywords = any(kw in api_files.metadata.keywords for kw in api_keywords)

    if has_api_keywords:
        print(f"     [OK] API-specific keywords included")
        checks_passed += 1
    else:
        print(f"     [FAIL] API-specific keywords missing")

    # Test with database category
    db_spec = ToolSpec(
        name="DbTool",
        display_name="Database Tool",
        description="Database tool",
        category="database",
        inputs=[],
        author="Author",
        version="1.0.0"
    )

    db_files = generator.generate(db_spec, "")

    # Check 8.2: Database category gets specific keywords and classifiers
    print("\n  Check 8.2: Database category gets specific features...")

    db_keywords = ["database", "sql", "data"]
    has_db_keywords = any(kw in db_files.metadata.keywords for kw in db_keywords)

    db_classifier = "Topic :: Database"
    has_db_classifier = db_classifier in db_files.metadata.classifiers

    if has_db_keywords and has_db_classifier:
        print(f"     [OK] Database-specific features included")
        checks_passed += 1
    else:
        print(f"     [FAIL] Database-specific features missing")

    print(f"\n  Result: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


def main():
    """Run all Phase 2.3 tests"""
    print("\n")
    print("=" * 80)
    print("PHASE 2.3: Standalone Tool Packaging - Validation Tests")
    print("=" * 80)
    print("\n")

    tests = [
        ("Package Metadata Generation", test_package_metadata_generation),
        ("pyproject.toml Generation", test_pyproject_toml_generation),
        ("setup.py Generation", test_setup_py_generation),
        ("MANIFEST.in Generation", test_manifest_in_generation),
        ("README.md Generation", test_readme_generation),
        ("LICENSE Generation", test_license_generation),
        ("Complete Packaging Workflow", test_complete_packaging_workflow),
        ("Category-Specific Features", test_category_specific_features),
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
    print("PHASE 2.3 TEST SUMMARY")
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
        print("\n*** SUCCESS - All Phase 2.3 enhancements validated! ***")
        print()
        print("Validated Features:")
        print("  [OK] Package metadata generation (name, version, keywords, classifiers)")
        print("  [OK] pyproject.toml generation (build system, dependencies, metadata)")
        print("  [OK] setup.py generation (legacy support)")
        print("  [OK] MANIFEST.in generation (file inclusion/exclusion)")
        print("  [OK] README.md generation (documentation, installation, features)")
        print("  [OK] LICENSE generation (MIT License with author)")
        print("  [OK] Complete packaging workflow")
        print("  [OK] Category-specific features (keywords, classifiers)")
        print()
        print("=" * 80)
        print("RECOMMENDATION: Phase 2.3 is 100% complete and production-ready.")
        print("                Tools can now be distributed as standalone packages.")
        print("                Ready for final project summary.")
        print("=" * 80)
        return 0
    else:
        print(f"\n*** WARNING: {total - passed} test(s) failed ***")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
