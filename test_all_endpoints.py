"""
Comprehensive Endpoint Testing Script

Tests all CrewAI Component Generator endpoints to verify:
- Phase 1: Dependency validation
- Phase 2: Manual implementation templates
- Phase 3: RAG functionality
- Phase 4: Pattern validation

Usage:
    python test_all_endpoints.py
    python test_all_endpoints.py --generator-port 8085 --index-port 8086
    python test_all_endpoints.py --generator-url http://localhost:8085 --index-url http://localhost:8086
"""

import requests
import json
import yaml
import argparse
import os
from datetime import datetime
from typing import Dict, Any


class EndpointTester:
    """Test all CrewAI generator endpoints"""

    def __init__(self, generator_url: str = "http://localhost:8085", index_url: str = "http://localhost:8086"):
        self.generator_url = generator_url
        self.index_url = index_url
        self.test_results = []

    def print_section(self, title: str):
        """Print a test section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")

    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({"test": test_name, "passed": passed, "details": details})

    def test_health_endpoints(self):
        """Test health check endpoints"""
        self.print_section("TEST 1: Health Check Endpoints")

        # Test component-generator health
        try:
            response = requests.get(f"{self.generator_url}/api/crewai/component-generator/health", timeout=5)
            passed = response.status_code == 200
            self.print_result(
                "Generator Health Check",
                passed,
                f"Status: {response.status_code}, Response: {response.json()}"
            )
        except Exception as e:
            self.print_result("Generator Health Check", False, f"Error: {str(e)}")

        # Test component-index health
        try:
            response = requests.get(f"{self.index_url}/api/crewai/component-index/health", timeout=5)
            passed = response.status_code == 200
            self.print_result(
                "Index Health Check",
                passed,
                f"Status: {response.status_code}, Response: {response.json()}"
            )
        except Exception as e:
            self.print_result("Index Health Check", False, f"Error: {str(e)}")

    def test_feasibility_endpoint(self):
        """Test feasibility assessment endpoint"""
        self.print_section("TEST 2: Feasibility Assessment Endpoint")

        spec_dict = {
            "name": "TestTool",
            "display_name": "Test Tool",
            "description": "A simple test tool for feasibility check",
            "category": "test",
            "version": "1.0.0",
            "author": "Test",
            "requirements": ["Must be simple", "Must use Python"],
            "inputs": [],
            "config_params": [],
            "dependencies": ["requests", "json"]
        }

        spec_yaml = yaml.dump(spec_dict)

        try:
            response = requests.post(
                f"{self.generator_url}/api/crewai/component-generator/assess",
                json={"spec": spec_yaml},
                timeout=30
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Feasibility Assessment",
                passed,
                f"Feasible: {data.get('feasible', 'N/A')}, Confidence: {data.get('confidence', 'N/A')}"
            )

            if passed:
                print(f"   Complexity: {data.get('complexity', 'N/A')}")
                print(f"   Issues: {len(data.get('issues', []))}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")

        except Exception as e:
            self.print_result("Feasibility Assessment", False, f"Error: {str(e)}")

    def test_sample_generation(self):
        """Test sample tool generation endpoint"""
        self.print_section("TEST 3: Sample Tool Generation (/generate/sample)")

        try:
            response = requests.post(
                f"{self.generator_url}/api/crewai/component-generator/generate/sample",
                timeout=60
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Sample Tool Generation",
                passed,
                f"Generated: {passed}"
            )

            if passed:
                print(f"   Code Size: {len(data.get('code', ''))} bytes")
                print(f"   Has Documentation: {len(data.get('documentation', '')) > 0}")

        except Exception as e:
            self.print_result("Sample Tool Generation", False, f"Error: {str(e)}")

    def test_generation_with_supported_deps(self):
        """Test generation with all supported dependencies (Phase 1)"""
        self.print_section("TEST 4: Generation with SUPPORTED Dependencies (Phase 1)")

        spec_dict = {
            "name": "HTTPFetchTool",
            "display_name": "HTTP Fetch Tool",
            "description": "Fetches data from HTTP endpoints",
            "category": "web",
            "version": "1.0.0",
            "author": "Test",
            "requirements": ["Fetch data from URLs", "Parse JSON responses"],
            "inputs": [
                {
                    "name": "url",
                    "type": "str",
                    "description": "URL to fetch",
                    "required": True
                }
            ],
            "config_params": [],
            "dependencies": ["requests", "json"]  # Both supported
        }

        # Convert to YAML string
        spec_yaml = yaml.dump(spec_dict)

        try:
            response = requests.post(
                f"{self.generator_url}/api/crewai/component-generator/generate",
                json={"spec": spec_yaml},
                timeout=90
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Generation with Supported Deps",
                passed,
                f"Generated: {passed}"
            )

            if passed:
                print(f"   Code Size: {len(data.get('code', ''))} bytes")
                print(f"   Has Documentation: {len(data.get('documentation', '')) > 0}")

                # Check code structure
                code = data.get('code', '')
                has_base_tool = 'BaseTool' in code
                has_run_method = 'def _run(' in code

                print(f"   Has BaseTool: {has_base_tool}")
                print(f"   Has _run(): {has_run_method}")

        except Exception as e:
            self.print_result("Generation with Supported Deps", False, f"Error: {str(e)}")

    def test_generation_with_unsupported_deps(self):
        """Test generation with UNsupported dependencies (Phase 1 + Phase 2)"""
        self.print_section("TEST 5: Generation with UNSUPPORTED Dependencies (Phase 1 + 2)")

        spec_dict = {
            "name": "CustomHTTPTool",
            "display_name": "Custom HTTP Tool",
            "description": "HTTP client using unsupported library",
            "category": "web",
            "version": "1.0.0",
            "author": "Test",
            "requirements": ["Make HTTP requests", "Handle responses"],
            "inputs": [
                {
                    "name": "endpoint",
                    "type": "str",
                    "description": "API endpoint",
                    "required": True
                }
            ],
            "config_params": [],
            "dependencies": ["fake_http_library", "json"]  # fake_http_library is unsupported
        }

        spec_yaml = yaml.dump(spec_dict)

        try:
            response = requests.post(
                f"{self.generator_url}/api/crewai/component-generator/generate",
                json={"spec": spec_yaml},
                timeout=90
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Generation with Unsupported Deps",
                passed,
                f"Generated: {passed}"
            )

            if passed:
                print(f"   Code Size: {len(data.get('code', ''))} bytes")
                print(f"   Has Documentation: {len(data.get('documentation', '')) > 0}")

                # Check if code uses stdlib
                code = data.get('code', '')
                has_urllib = 'urllib' in code or 'http.client' in code
                has_base_tool = 'BaseTool' in code
                has_run_method = 'def _run(' in code

                print(f"   Uses stdlib HTTP: {has_urllib}")
                print(f"   Has BaseTool: {has_base_tool}")
                print(f"   Has _run(): {has_run_method}")

        except Exception as e:
            self.print_result("Generation with Unsupported Deps", False, f"Error: {str(e)}")

    def test_pattern_validation(self):
        """Test pattern validation (Phase 4)"""
        self.print_section("TEST 6: Pattern Validation (Phase 4)")

        # Generate a tool and check pattern validation
        spec_dict = {
            "name": "PatternTestTool",
            "display_name": "Pattern Test Tool",
            "description": "Tool to test pattern validation",
            "category": "test",
            "version": "1.0.0",
            "author": "Test",
            "requirements": ["Simple functionality"],
            "inputs": [
                {
                    "name": "input_data",
                    "type": "str",
                    "description": "Input data",
                    "required": True
                }
            ],
            "config_params": [],
            "dependencies": ["json"]
        }

        spec_yaml = yaml.dump(spec_dict)

        try:
            response = requests.post(
                f"{self.generator_url}/api/crewai/component-generator/generate",
                json={"spec": spec_yaml},
                timeout=90
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Pattern Validation Integration",
                passed,
                f"Generated: {passed}"
            )

            if passed:
                print(f"   Code Size: {len(data.get('code', ''))} bytes")
                print(f"   Has Documentation: {len(data.get('documentation', '')) > 0}")

                # Check code structure
                code = data.get('code', '')
                has_base_tool = 'BaseTool' in code
                has_run_method = 'def _run(' in code
                has_args_schema = 'args_schema' in code

                print(f"   Has BaseTool: {has_base_tool}")
                print(f"   Has _run(): {has_run_method}")
                print(f"   Has args_schema: {has_args_schema}")

        except Exception as e:
            self.print_result("Pattern Validation Integration", False, f"Error: {str(e)}")

    def test_rag_patterns_endpoint(self):
        """Test RAG pattern retrieval (Phase 3)"""
        self.print_section("TEST 7: RAG Pattern Retrieval (Phase 3)")

        payload = {
            "description": "A tool for web scraping",
            "category": "web",
            "n_results": 3
        }

        try:
            response = requests.post(
                f"{self.index_url}/api/crewai/component-index/patterns/similar",
                json=payload,
                timeout=10
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "RAG Pattern Retrieval",
                passed,
                f"Results: {data.get('results_count', 0)}"
            )

            if passed and data.get('results'):
                print(f"   Found patterns:")
                for i, result in enumerate(data.get('results', [])[:3], 1):
                    print(f"     {i}. {result.get('name', 'Unknown')} (similarity: {result.get('similarity', 'N/A')})")

        except Exception as e:
            self.print_result("RAG Pattern Retrieval", False, f"Error: {str(e)}")

    def test_index_tool_endpoint(self):
        """Test tool indexing endpoint"""
        self.print_section("TEST 8: Tool Indexing Endpoint")

        tool_data = {
            "name": "TestIndexTool",
            "description": "A test tool for indexing",
            "category": "test",
            "code": """
from crewai.tools import BaseTool
from pydantic import BaseModel

class TestIndexTool(BaseTool):
    name: str = "Test Index Tool"
    description: str = "A test tool"

    def _run(self) -> str:
        return "test"
"""
        }

        try:
            response = requests.post(
                f"{self.index_url}/api/crewai/component-index/patterns/index",
                json=tool_data,
                timeout=10
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Tool Indexing",
                passed,
                f"Success: {data.get('success', False)}"
            )

            if passed:
                print(f"   Message: {data.get('message', 'N/A')}")

        except Exception as e:
            self.print_result("Tool Indexing", False, f"Error: {str(e)}")

    def test_collection_stats(self):
        """Test collection statistics endpoint"""
        self.print_section("TEST 9: Collection Statistics")

        try:
            response = requests.get(
                f"{self.index_url}/api/crewai/component-index/patterns/stats",
                timeout=10
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}

            self.print_result(
                "Collection Stats",
                passed,
                f"Total patterns: {data.get('total_patterns', 0)}"
            )

            if passed:
                print(f"   Collection: {data.get('collection_name', 'N/A')}")

        except Exception as e:
            self.print_result("Collection Stats", False, f"Error: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        self.print_section("TEST SUMMARY")

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"[PASS] Passed: {passed}")
        print(f"[FAIL] Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  [FAIL] {result['test']}")
                    if result['details']:
                        print(f"     {result['details']}")

        print("\n" + "=" * 80)

    def run_all_tests(self):
        """Run all endpoint tests"""
        print("\n" + "=" * 80)
        print("  CREWAI COMPONENT GENERATOR - COMPREHENSIVE ENDPOINT TESTING")
        print("  Testing All Phases: 1 (Deps) + 2 (Templates) + 3 (RAG) + 4 (Patterns)")
        print("=" * 80)

        # Run all tests
        self.test_health_endpoints()
        self.test_feasibility_endpoint()
        self.test_sample_generation()
        self.test_generation_with_supported_deps()
        self.test_generation_with_unsupported_deps()
        self.test_pattern_validation()
        self.test_rag_patterns_endpoint()
        self.test_index_tool_endpoint()
        self.test_collection_stats()

        # Print summary
        self.print_summary()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test CrewAI Component Generator and Index endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test default ports (Docker mode)
  python test_all_endpoints.py

  # Test custom ports (standalone mode)
  python test_all_endpoints.py --generator-port 8085 --index-port 8086

  # Test with full URLs
  python test_all_endpoints.py --generator-url http://localhost:9085 --index-url http://localhost:9086

  # Use environment variables
  export GENERATOR_URL=http://localhost:8085
  export INDEX_URL=http://localhost:8086
  python test_all_endpoints.py
        """
    )

    parser.add_argument(
        "--generator-url",
        default=os.getenv("GENERATOR_URL", "http://localhost:8085"),
        help="Full URL of the component-generator service (default: http://localhost:8085)"
    )

    parser.add_argument(
        "--index-url",
        default=os.getenv("INDEX_URL", "http://localhost:8086"),
        help="Full URL of the component-index service (default: http://localhost:8086)"
    )

    parser.add_argument(
        "--generator-port",
        type=int,
        help="Port for component-generator (overrides --generator-url)"
    )

    parser.add_argument(
        "--index-port",
        type=int,
        help="Port for component-index (overrides --index-url)"
    )

    args = parser.parse_args()

    # Port arguments override URL arguments
    generator_url = args.generator_url
    index_url = args.index_url

    if args.generator_port:
        generator_url = f"http://localhost:{args.generator_port}"

    if args.index_port:
        index_url = f"http://localhost:{args.index_port}"

    print(f"\nTesting endpoints:")
    print(f"  Generator: {generator_url}")
    print(f"  Index:     {index_url}\n")

    tester = EndpointTester(generator_url=generator_url, index_url=index_url)
    tester.run_all_tests()
