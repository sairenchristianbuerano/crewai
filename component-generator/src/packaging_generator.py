"""
Packaging Generator for CrewAI Tools

Automatically generates packaging files for standalone tool distribution:
- pyproject.toml for Poetry/pip
- setup.py for legacy support
- MANIFEST.in for package data
- Package metadata

Phase: 2.3 - Standalone Tool Packaging
Author: Component Factory
Date: 2025-12-21
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import structlog
from base_classes import ToolSpec


logger = structlog.get_logger().bind(component="packaging_generator")


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PackageMetadata:
    """
    Package metadata for tool distribution

    Attributes:
        name: Package name (e.g., 'crewai-tool-web-scraper')
        version: Package version (e.g., '1.0.0')
        description: Short package description
        author: Package author
        author_email: Author's email
        license: License type (e.g., 'MIT')
        python_requires: Python version requirement
        dependencies: List of package dependencies
        keywords: List of keywords for package discovery
        classifiers: PyPI classifiers
        homepage: Project homepage URL
        repository: Source repository URL
    """
    name: str
    version: str
    description: str
    author: str
    author_email: Optional[str] = None
    license: str = "MIT"
    python_requires: str = ">=3.8"
    dependencies: List[str] = None
    keywords: List[str] = None
    classifiers: List[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.keywords is None:
            self.keywords = []
        if self.classifiers is None:
            self.classifiers = []


@dataclass
class PackagingFiles:
    """
    Complete set of packaging files

    Attributes:
        pyproject_toml: pyproject.toml content
        setup_py: setup.py content (legacy support)
        manifest_in: MANIFEST.in content
        readme_md: README.md content
        license_file: LICENSE content
        metadata: PackageMetadata object
    """
    pyproject_toml: str
    setup_py: str
    manifest_in: str
    readme_md: str
    license_file: str
    metadata: PackageMetadata


# ============================================================================
# PACKAGING GENERATOR
# ============================================================================

class PackagingGenerator:
    """
    Generates packaging files for standalone tool distribution

    Creates all necessary files for distributing tools as Python packages:
    - pyproject.toml (modern Python packaging)
    - setup.py (legacy compatibility)
    - MANIFEST.in (package data)
    - README.md (package documentation)
    - LICENSE (MIT license by default)
    """

    def __init__(self):
        """Initialize the packaging generator"""
        self.logger = logger.bind(component="packaging_generator")

    def generate(self, spec: ToolSpec, tool_code: str) -> PackagingFiles:
        """
        Generate complete packaging files for a tool

        Args:
            spec: ToolSpec object with tool specification
            tool_code: Generated tool code

        Returns:
            PackagingFiles object with all packaging content
        """
        self.logger.info("Generating packaging files", tool_name=spec.name)

        # Generate metadata
        metadata = self._generate_metadata(spec)

        # Generate all packaging files
        pyproject_toml = self._generate_pyproject_toml(metadata, spec)
        setup_py = self._generate_setup_py(metadata, spec)
        manifest_in = self._generate_manifest_in(spec)
        readme_md = self._generate_readme(spec)
        license_file = self._generate_license(metadata)

        files = PackagingFiles(
            pyproject_toml=pyproject_toml,
            setup_py=setup_py,
            manifest_in=manifest_in,
            readme_md=readme_md,
            license_file=license_file,
            metadata=metadata
        )

        self.logger.info("Packaging files generated",
            tool_name=spec.name,
            package_name=metadata.name
        )

        return files

    def _generate_metadata(self, spec: ToolSpec) -> PackageMetadata:
        """Generate package metadata from tool spec"""
        # Convert tool name to package name
        snake_name = self._to_snake_case(spec.name)
        package_name = f"crewai-tool-{snake_name}"

        # Generate keywords
        keywords = [
            "crewai",
            "tool",
            spec.category,
            "ai",
            "agent"
        ]

        # Add category-specific keywords
        if spec.category == "api":
            keywords.extend(["api", "http", "rest"])
        elif spec.category == "database":
            keywords.extend(["database", "sql", "data"])
        elif spec.category == "file":
            keywords.extend(["file", "filesystem", "io"])
        elif spec.category == "web":
            keywords.extend(["web", "scraping", "html"])

        # Generate classifiers
        classifiers = [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ]

        # Add category-specific classifiers
        if spec.category == "api":
            classifiers.append("Topic :: Internet :: WWW/HTTP")
        elif spec.category == "database":
            classifiers.append("Topic :: Database")

        # Ensure crewai and pydantic are in dependencies
        dependencies = list(spec.dependencies) if spec.dependencies else []
        if "crewai" not in dependencies:
            dependencies.insert(0, "crewai>=0.1.0")
        if "pydantic" not in dependencies:
            dependencies.insert(1, "pydantic>=2.0.0")

        return PackageMetadata(
            name=package_name,
            version=spec.version,
            description=spec.description,
            author=spec.author,
            author_email=None,  # Could be extracted from spec if available
            license="MIT",
            python_requires=">=3.8",
            dependencies=dependencies,
            keywords=keywords,
            classifiers=classifiers
        )

    def _generate_pyproject_toml(self, metadata: PackageMetadata, spec: ToolSpec) -> str:
        """Generate pyproject.toml file"""
        lines = []

        # Build system
        lines.append("[build-system]")
        lines.append('requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]')
        lines.append('build-backend = "setuptools.build_meta"')
        lines.append("")

        # Project metadata
        lines.append("[project]")
        lines.append(f'name = "{metadata.name}"')
        lines.append(f'version = "{metadata.version}"')
        lines.append(f'description = "{metadata.description}"')
        lines.append('readme = "README.md"')
        lines.append(f'requires-python = "{metadata.python_requires}"')
        lines.append(f'license = {{text = "{metadata.license}"}}')
        lines.append("")

        # Authors
        lines.append("authors = [")
        if metadata.author_email:
            lines.append(f'    {{name = "{metadata.author}", email = "{metadata.author_email}"}}')
        else:
            lines.append(f'    {{name = "{metadata.author}"}}')
        lines.append("]")
        lines.append("")

        # Keywords
        if metadata.keywords:
            lines.append("keywords = [")
            for keyword in metadata.keywords:
                lines.append(f'    "{keyword}",')
            lines.append("]")
            lines.append("")

        # Classifiers
        if metadata.classifiers:
            lines.append("classifiers = [")
            for classifier in metadata.classifiers:
                lines.append(f'    "{classifier}",')
            lines.append("]")
            lines.append("")

        # Dependencies
        if metadata.dependencies:
            lines.append("dependencies = [")
            for dep in metadata.dependencies:
                lines.append(f'    "{dep}",')
            lines.append("]")
            lines.append("")

        # URLs
        lines.append("[project.urls]")
        if metadata.homepage:
            lines.append(f'Homepage = "{metadata.homepage}"')
        if metadata.repository:
            lines.append(f'Repository = "{metadata.repository}"')
        lines.append('Documentation = "https://github.com/crewai-tools"')
        lines.append("")

        # Tool configuration
        lines.append("[tool.setuptools]")
        lines.append("packages = [")
        snake_name = self._to_snake_case(spec.name)
        lines.append(f'    "{snake_name}",')
        lines.append("]")
        lines.append("")

        lines.append("[tool.setuptools.package-data]")
        lines.append(f'"{snake_name}" = ["py.typed"]')
        lines.append("")

        return "\n".join(lines)

    def _generate_setup_py(self, metadata: PackageMetadata, spec: ToolSpec) -> str:
        """Generate setup.py for legacy support"""
        lines = []

        lines.append("#!/usr/bin/env python")
        lines.append('"""')
        lines.append(f"{spec.display_name} - CrewAI Tool")
        lines.append("")
        lines.append(metadata.description)
        lines.append('"""')
        lines.append("")
        lines.append("from setuptools import setup, find_packages")
        lines.append("")
        lines.append('with open("README.md", "r", encoding="utf-8") as fh:')
        lines.append("    long_description = fh.read()")
        lines.append("")
        lines.append("setup(")
        lines.append(f'    name="{metadata.name}",')
        lines.append(f'    version="{metadata.version}",')
        lines.append(f'    author="{metadata.author}",')
        if metadata.author_email:
            lines.append(f'    author_email="{metadata.author_email}",')
        lines.append(f'    description="{metadata.description}",')
        lines.append('    long_description=long_description,')
        lines.append('    long_description_content_type="text/markdown",')
        lines.append(f'    license="{metadata.license}",')
        lines.append('    packages=find_packages(),')
        lines.append(f'    python_requires="{metadata.python_requires}",')

        # Dependencies
        if metadata.dependencies:
            lines.append("    install_requires=[")
            for dep in metadata.dependencies:
                lines.append(f'        "{dep}",')
            lines.append("    ],")

        # Classifiers
        if metadata.classifiers:
            lines.append("    classifiers=[")
            for classifier in metadata.classifiers:
                lines.append(f'        "{classifier}",')
            lines.append("    ],")

        # Keywords
        if metadata.keywords:
            keywords_str = ", ".join(metadata.keywords)
            lines.append(f'    keywords="{keywords_str}",')

        lines.append("    package_data={")
        snake_name = self._to_snake_case(spec.name)
        lines.append(f'        "{snake_name}": ["py.typed"],')
        lines.append("    },")
        lines.append(")")
        lines.append("")

        return "\n".join(lines)

    def _generate_manifest_in(self, spec: ToolSpec) -> str:
        """Generate MANIFEST.in file"""
        lines = []

        lines.append("# Include documentation")
        lines.append("include README.md")
        lines.append("include LICENSE")
        lines.append("")
        lines.append("# Include package data")
        lines.append("include pyproject.toml")
        lines.append("include setup.py")
        lines.append("")
        lines.append("# Include type information")
        lines.append("recursive-include */py.typed")
        lines.append("")
        lines.append("# Exclude development files")
        lines.append("global-exclude __pycache__")
        lines.append("global-exclude *.py[cod]")
        lines.append("global-exclude *~")
        lines.append("global-exclude .DS_Store")
        lines.append("")

        return "\n".join(lines)

    def _generate_readme(self, spec: ToolSpec) -> str:
        """Generate README.md for the package"""
        snake_name = self._to_snake_case(spec.name)
        package_name = f"crewai-tool-{snake_name}"

        lines = []

        # Title and badges
        lines.append(f"# {spec.display_name}")
        lines.append("")
        lines.append(f"[![PyPI version](https://badge.fury.io/py/{package_name}.svg)](https://badge.fury.io/py/{package_name})")
        lines.append(f"[![Python](https://img.shields.io/pypi/pyversions/{package_name}.svg)](https://pypi.org/project/{package_name}/)")
        lines.append(f"[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)")
        lines.append("")

        # Description
        lines.append("## Description")
        lines.append("")
        lines.append(spec.description)
        lines.append("")

        # Features
        if spec.requirements:
            lines.append("## Features")
            lines.append("")
            for req in spec.requirements:
                lines.append(f"- {req}")
            lines.append("")

        # Installation
        lines.append("## Installation")
        lines.append("")
        lines.append("```bash")
        lines.append(f"pip install {package_name}")
        lines.append("```")
        lines.append("")

        # Quick Start
        lines.append("## Quick Start")
        lines.append("")
        lines.append("```python")
        lines.append(f"from {snake_name} import {spec.name}")
        lines.append("")
        lines.append("# Initialize the tool")
        lines.append(f"tool = {spec.name}()")
        lines.append("")
        lines.append("# Use in your CrewAI workflow")
        lines.append("from crewai import Agent")
        lines.append("")
        lines.append("agent = Agent(")
        lines.append(f'    role="{spec.category.title()} Specialist",')
        lines.append(f'    goal="Perform {spec.category} operations",')
        lines.append("    tools=[tool],")
        lines.append("    verbose=True")
        lines.append(")")
        lines.append("```")
        lines.append("")

        # Dependencies
        if spec.dependencies:
            lines.append("## Dependencies")
            lines.append("")
            for dep in spec.dependencies:
                lines.append(f"- `{dep}`")
            lines.append("")

        # License
        lines.append("## License")
        lines.append("")
        lines.append("MIT License - see LICENSE file for details")
        lines.append("")

        # Author
        lines.append("## Author")
        lines.append("")
        lines.append(spec.author)
        lines.append("")

        # Links
        lines.append("## Links")
        lines.append("")
        lines.append("- [CrewAI Documentation](https://docs.crewai.com)")
        lines.append("- [PyPI Package](https://pypi.org/project/" + package_name + "/)")
        lines.append("")

        return "\n".join(lines)

    def _generate_license(self, metadata: PackageMetadata) -> str:
        """Generate MIT LICENSE file"""
        from datetime import datetime

        year = datetime.now().year
        author = metadata.author

        license_text = f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        return license_text

    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_packaging(spec: ToolSpec, tool_code: str) -> PackagingFiles:
    """
    Quick packaging generation function

    Args:
        spec: ToolSpec object
        tool_code: Generated tool code

    Returns:
        PackagingFiles object
    """
    generator = PackagingGenerator()
    return generator.generate(spec, tool_code)


def save_packaging_files(files: PackagingFiles, output_dir: str) -> None:
    """
    Save packaging files to directory

    Args:
        files: PackagingFiles object
        output_dir: Directory to save files
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    # Save each file
    with open(os.path.join(output_dir, "pyproject.toml"), 'w', encoding='utf-8') as f:
        f.write(files.pyproject_toml)

    with open(os.path.join(output_dir, "setup.py"), 'w', encoding='utf-8') as f:
        f.write(files.setup_py)

    with open(os.path.join(output_dir, "MANIFEST.in"), 'w', encoding='utf-8') as f:
        f.write(files.manifest_in)

    with open(os.path.join(output_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(files.readme_md)

    with open(os.path.join(output_dir, "LICENSE"), 'w', encoding='utf-8') as f:
        f.write(files.license_file)


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    from base_classes import ToolSpec, ToolInputParameter

    # Example usage
    spec = ToolSpec(
        name="WebScraperTool",
        display_name="Web Scraper",
        description="Scrape and extract data from web pages",
        category="web",
        requirements=[
            "Extract text content from web pages",
            "Support CSS selectors",
            "Handle dynamic content"
        ],
        inputs=[
            ToolInputParameter(
                name="url",
                type="str",
                description="URL of the web page to scrape",
                required=True
            )
        ],
        dependencies=["requests", "beautifulsoup4"],
        author="Component Factory",
        version="1.0.0"
    )

    # Generate packaging
    generator = PackagingGenerator()
    files = generator.generate(spec, "")

    # Print pyproject.toml
    print("=== pyproject.toml ===")
    print(files.pyproject_toml)
    print("\n=== Package Name ===")
    print(files.metadata.name)
