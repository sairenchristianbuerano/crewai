"""
RAG (Retrieval-Augmented Generation) engine for crewAI tool pattern search

Uses ChromaDB for vector embeddings and semantic search over tool patterns.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class CrewAIRAGEngine:
    """RAG engine for semantic search over crewAI tool patterns"""

    def __init__(
        self,
        tools_directory: str = "/app/data/crewai_components/tools",
        persist_directory: str = "/app/data/chromadb"
    ):
        """
        Initialize the RAG engine

        Args:
            tools_directory: Directory containing reference tool implementations
            persist_directory: Directory for ChromaDB persistence
        """
        self.tools_dir = Path(tools_directory)
        self.persist_dir = Path(persist_directory)
        self.logger = logger.bind(component="crewai_rag")

        # Initialize ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings

            self.client = chromadb.Client(Settings(
                persist_directory=str(self.persist_dir),
                anonymized_telemetry=False
            ))

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="crewai_tools",
                metadata={"description": "CrewAI tool patterns for RAG"}
            )

            self.logger.info("ChromaDB initialized", persist_dir=str(self.persist_dir))

        except ImportError:
            self.logger.error("ChromaDB not installed - pip install chromadb")
            raise
        except Exception as e:
            self.logger.error("Failed to initialize ChromaDB", error=str(e))
            raise

    def index_tools(self, force_reindex: bool = False) -> int:
        """
        Index all tools from the tools directory

        Args:
            force_reindex: If True, clear existing index and reindex all tools

        Returns:
            Number of tools indexed
        """
        if force_reindex:
            self.logger.info("Force reindex requested - clearing collection")
            self.client.delete_collection("crewai_tools")
            self.collection = self.client.create_collection(
                name="crewai_tools",
                metadata={"description": "CrewAI tool patterns for RAG"}
            )

        # Check if already indexed
        existing_count = self.collection.count()
        if existing_count > 0 and not force_reindex:
            self.logger.info("Tools already indexed", count=existing_count)
            return existing_count

        # Find all Python files in tools directory
        if not self.tools_dir.exists():
            self.logger.warning("Tools directory does not exist", path=str(self.tools_dir))
            return 0

        tool_files = list(self.tools_dir.glob("*.py"))
        tool_files = [f for f in tool_files if not f.name.startswith("__")]

        if not tool_files:
            self.logger.warning("No tool files found", path=str(self.tools_dir))
            return 0

        self.logger.info(f"Found {len(tool_files)} tool files to index")

        indexed_count = 0

        for tool_file in tool_files:
            try:
                # Read tool code
                with open(tool_file, 'r') as f:
                    code = f.read()

                # Extract metadata
                metadata = self._extract_tool_metadata(code, tool_file.stem)

                # Add to collection
                self.collection.add(
                    ids=[tool_file.stem],
                    documents=[code],
                    metadatas=[metadata]
                )

                indexed_count += 1
                self.logger.debug(f"Indexed tool: {tool_file.stem}")

            except Exception as e:
                self.logger.warning(f"Failed to index {tool_file.name}", error=str(e))

        self.logger.info(f"Indexing complete", indexed=indexed_count, total=len(tool_files))
        return indexed_count

    def _extract_tool_metadata(self, code: str, filename: str) -> Dict[str, Any]:
        """Extract metadata from tool code"""
        import re

        metadata = {
            "name": filename,
            "category": "custom"
        }

        # Try to extract class name
        class_match = re.search(r'class\s+(\w+)\(BaseTool\)', code)
        if class_match:
            metadata["name"] = class_match.group(1)

        # Try to extract description
        desc_match = re.search(r'description:\s*str\s*=\s*["\']([^"\']+)["\']', code)
        if desc_match:
            metadata["description"] = desc_match.group(1)

        # Detect category based on code patterns
        if 'requests' in code or 'http' in code.lower():
            metadata["category"] = "api"
        elif 'search' in code.lower() or 'ddg' in code.lower():
            metadata["category"] = "search"
        elif 'file' in code.lower() or 'write' in code.lower():
            metadata["category"] = "file"
        elif 'database' in code.lower() or 'sql' in code.lower():
            metadata["category"] = "database"

        return metadata

    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for tools using semantic search

        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {"category": "api"})

        Returns:
            List of matching tools with similarity scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters
            )

            # Format results
            formatted_results = []

            if results['ids'] and len(results['ids']) > 0:
                for i, tool_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "name": tool_id,
                        "code": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "similarity": 1.0 - (results['distances'][0][i] if results.get('distances') else 0.0)
                    })

            return formatted_results

        except Exception as e:
            self.logger.error("Search failed", error=str(e))
            return []

    def find_similar_tools(
        self,
        description: str,
        category: Optional[str] = None,
        input_types: Optional[List[str]] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find tools similar to a description

        Args:
            description: Tool description to find similar patterns for
            category: Optional category filter
            input_types: Optional input type filters
            n_results: Number of results

        Returns:
            List of similar tools
        """
        filters = {}
        if category:
            filters["category"] = category

        return self.search(description, n_results, filters)

    def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool by name"""
        try:
            result = self.collection.get(ids=[name])

            if result['ids']:
                return {
                    "name": result['ids'][0],
                    "code": result['documents'][0] if result['documents'] else "",
                    "metadata": result['metadatas'][0] if result['metadatas'] else {}
                }

            return None

        except Exception as e:
            self.logger.error("Failed to get tool", name=name, error=str(e))
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics"""
        try:
            count = self.collection.count()

            return {
                "total_tools": count,
                "has_embeddings": count > 0
            }

        except Exception as e:
            self.logger.error("Failed to get stats", error=str(e))
            return {"total_tools": 0, "has_embeddings": False}
