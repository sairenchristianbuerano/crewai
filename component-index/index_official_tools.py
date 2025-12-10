"""
Index Official CrewAI Tools into ChromaDB

This script indexes all 73 official crewAI tools from the official repository
into ChromaDB for enhanced RAG pattern matching.

Source: C:\Users\Joana\Desktop\sairen-files\github\env\crewAI
Target: component-index ChromaDB (enriching from 7 to 80+ tools)

Usage:
    python index_official_tools.py

Author: CrewAI Tool Generator Team
Date: 2025-12-11
Phase: 3.1 - RAG Enrichment
"""

import os
import sys
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("Error: chromadb not installed. Run: pip install chromadb")
    sys.exit(1)


logger = structlog.get_logger()


class OfficialToolIndexer:
    """
    Indexes official crewAI tools into ChromaDB

    Scans the official crewAI repository and extracts:
    - Tool class definitions
    - Tool configurations (name, description, args_schema)
    - Implementation code
    - Metadata (category, file path, etc.)
    """

    def __init__(
        self,
        official_repo_path: str,
        chroma_db_path: str = "/app/data/chroma",
        collection_name: str = "crewai_patterns"
    ):
        """
        Initialize the indexer

        Args:
            official_repo_path: Path to official crewAI repository
            chroma_db_path: Path to ChromaDB persistence directory
            collection_name: ChromaDB collection name
        """
        self.official_repo_path = Path(official_repo_path)
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.logger = logger.bind(component="official_tool_indexer")

        if not self.official_repo_path.exists():
            raise ValueError(f"Official repo path not found: {official_repo_path}")

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "CrewAI tool patterns for RAG"}
        )

        self.logger.info(
            "Indexer initialized",
            repo_path=str(self.official_repo_path),
            collection=collection_name,
            existing_count=self.collection.count()
        )

    def find_tool_files(self) -> List[Path]:
        """
        Find all tool Python files in the official repository

        Returns:
            List of Path objects pointing to tool files
        """
        self.logger.info("Scanning for tool files...")

        # Primary location: lib/crewai-tools/src/crewai_tools/tools/
        tools_dir = self.official_repo_path / "lib" / "crewai-tools" / "src" / "crewai_tools" / "tools"

        if not tools_dir.exists():
            self.logger.warning(
                "Tools directory not found",
                expected_path=str(tools_dir)
            )
            return []

        # Find all Python files in tool directories
        tool_files = []

        for tool_dir in tools_dir.iterdir():
            if not tool_dir.is_dir():
                continue

            # Look for *_tool.py files
            for py_file in tool_dir.glob("*_tool.py"):
                tool_files.append(py_file)

        self.logger.info(
            "Found tool files",
            count=len(tool_files)
        )

        return tool_files

    def extract_tool_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract tool information from Python file

        Args:
            file_path: Path to tool Python file

        Returns:
            Dictionary with tool information or None if extraction failed
        """
        try:
            # Read file content
            code = file_path.read_text(encoding='utf-8')

            # Parse AST
            tree = ast.parse(code)

            # Find BaseTool subclass
            tool_class = None
            tool_name = None

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from BaseTool
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'BaseTool':
                            tool_class = node
                            tool_name = node.name
                            break

                    if tool_class:
                        break

            if not tool_class:
                self.logger.debug(
                    "No BaseTool class found",
                    file=file_path.name
                )
                return None

            # Extract tool metadata
            name = self._extract_class_attribute(tool_class, 'name') or tool_name
            description = self._extract_class_attribute(tool_class, 'description') or ""

            # Determine category from path
            category = file_path.parent.name.replace('_tool', '').replace('_', ' ').title()

            # Build tool info
            tool_info = {
                'name': name,
                'class_name': tool_name,
                'description': description,
                'category': category,
                'file_path': str(file_path.relative_to(self.official_repo_path)),
                'code': code,
                'source': 'official_crewai',
                'version': '1.5.0'  # Current crewAI version
            }

            self.logger.debug(
                "Extracted tool info",
                name=tool_name,
                file=file_path.name
            )

            return tool_info

        except Exception as e:
            self.logger.error(
                "Failed to extract tool info",
                file=file_path.name,
                error=str(e)
            )
            return None

    def _extract_class_attribute(self, class_node: ast.ClassDef, attr_name: str) -> Optional[str]:
        """
        Extract string attribute value from class definition

        Args:
            class_node: AST ClassDef node
            attr_name: Attribute name to extract

        Returns:
            Attribute value as string or None
        """
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign):
                # Type-annotated assignment: name: str = "value"
                if isinstance(node.target, ast.Name) and node.target.id == attr_name:
                    if isinstance(node.value, ast.Constant):
                        return str(node.value.value)
            elif isinstance(node, ast.Assign):
                # Regular assignment: name = "value"
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == attr_name:
                        if isinstance(node.value, ast.Constant):
                            return str(node.value.value)

        return None

    def index_tools(self, tools: List[Dict[str, Any]]) -> int:
        """
        Index tools into ChromaDB

        Args:
            tools: List of tool dictionaries

        Returns:
            Number of tools successfully indexed
        """
        if not tools:
            return 0

        self.logger.info(
            "Indexing tools into ChromaDB...",
            count=len(tools)
        )

        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []

        for i, tool in enumerate(tools):
            # Create document text (for embedding)
            doc_text = f"{tool['name']}\n{tool['description']}\n{tool['category']}"

            # Create metadata
            metadata = {
                'name': tool['name'],
                'class_name': tool['class_name'],
                'description': tool['description'],
                'category': tool['category'],
                'file_path': tool['file_path'],
                'source': tool['source'],
                'version': tool['version']
            }

            # Create unique ID
            doc_id = f"official_{tool['class_name']}_{i}"

            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(doc_id)

        # Add to ChromaDB (also store the code separately)
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            # Store full code in a separate mapping (for retrieval)
            # Note: ChromaDB has document size limits, so we store code separately
            for i, tool in enumerate(tools):
                # Store code as document with special ID
                code_id = f"code_{tool['class_name']}_{i}"
                self.collection.add(
                    documents=[tool['code']],
                    metadatas=[{
                        'type': 'code',
                        'tool_name': tool['name'],
                        'class_name': tool['class_name']
                    }],
                    ids=[code_id]
                )

            self.logger.info(
                "Successfully indexed tools",
                count=len(tools),
                total_docs=self.collection.count()
            )

            return len(tools)

        except Exception as e:
            self.logger.error(
                "Failed to index tools",
                error=str(e)
            )
            return 0

    def run(self) -> Dict[str, Any]:
        """
        Run the full indexing process

        Returns:
            Summary dictionary with results
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting Official CrewAI Tools Indexing")
        self.logger.info("=" * 80)

        # Step 1: Find tool files
        tool_files = self.find_tool_files()

        if not tool_files:
            self.logger.error("No tool files found!")
            return {
                'success': False,
                'files_found': 0,
                'tools_extracted': 0,
                'tools_indexed': 0
            }

        # Step 2: Extract tool information
        tools = []
        for file_path in tool_files:
            tool_info = self.extract_tool_info(file_path)
            if tool_info:
                tools.append(tool_info)

        self.logger.info(
            f"Extracted {len(tools)} tools from {len(tool_files)} files"
        )

        # Step 3: Index tools
        indexed_count = self.index_tools(tools)

        # Step 4: Summary
        summary = {
            'success': indexed_count > 0,
            'files_found': len(tool_files),
            'tools_extracted': len(tools),
            'tools_indexed': indexed_count,
            'total_in_collection': self.collection.count(),
            'tool_names': [t['name'] for t in tools]
        }

        self.logger.info("=" * 80)
        self.logger.info("Indexing Complete!")
        self.logger.info("=" * 80)
        self.logger.info(f"Files found: {summary['files_found']}")
        self.logger.info(f"Tools extracted: {summary['tools_extracted']}")
        self.logger.info(f"Tools indexed: {summary['tools_indexed']}")
        self.logger.info(f"Total in collection: {summary['total_in_collection']}")
        self.logger.info("=" * 80)

        return summary


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("  Official CrewAI Tools Indexer")
    print("  Phase 3.1: RAG Enrichment")
    print("=" * 80 + "\n")

    # Configuration
    OFFICIAL_REPO_PATH = r"C:\Users\Joana\Desktop\sairen-files\github\env\crewAI"
    CHROMA_DB_PATH = "/app/data/chroma"  # Docker path

    # Check if running in Docker or local
    if not os.path.exists(CHROMA_DB_PATH):
        # Local development - use relative path
        CHROMA_DB_PATH = os.path.join(
            os.path.dirname(__file__),
            "data",
            "chroma"
        )
        print(f"Running locally, using ChromaDB path: {CHROMA_DB_PATH}\n")

    # Create indexer
    try:
        indexer = OfficialToolIndexer(
            official_repo_path=OFFICIAL_REPO_PATH,
            chroma_db_path=CHROMA_DB_PATH
        )

        # Run indexing
        summary = indexer.run()

        # Print summary
        if summary['success']:
            print("\n✅ Indexing completed successfully!")
            print(f"\nIndexed Tools ({summary['tools_indexed']}):")
            for i, name in enumerate(summary['tool_names'][:10], 1):
                print(f"  {i}. {name}")
            if len(summary['tool_names']) > 10:
                print(f"  ... and {len(summary['tool_names']) - 10} more")

        else:
            print("\n❌ Indexing failed!")

        return 0 if summary['success'] else 1

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
