"""
JSON-based storage for crewAI tool registry
"""

import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog

from models import ToolMetadata

logger = structlog.get_logger()


class ToolStorage:
    """JSON-based tool storage for registry"""

    def __init__(self, storage_path: str = "/app/data/components"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self.logger = logger.bind(storage="tool_index")

        # Initialize index if not exists
        if not self.index_file.exists():
            self._save_index({})
            self.logger.info("Initialized new tool index")

    def _load_index(self) -> Dict[str, Any]:
        """Load tool index from JSON"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("Failed to load index", error=str(e))
            return {}

    def _save_index(self, index: Dict[str, Any]):
        """Save tool index to JSON"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            self.logger.error("Failed to save index", error=str(e))
            raise

    def register_tool(self, metadata: ToolMetadata) -> ToolMetadata:
        """Register a new tool"""
        index = self._load_index()

        # Generate unique ID if not provided
        if not metadata.tool_id:
            metadata.tool_id = str(uuid.uuid4())

        # Add to index
        index[metadata.tool_id] = metadata.model_dump()

        self._save_index(index)
        self.logger.info("Tool registered", tool_id=metadata.tool_id, name=metadata.name)

        return metadata

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool by ID"""
        index = self._load_index()

        if tool_id not in index:
            return None

        return ToolMetadata(**index[tool_id])

    def get_tool_by_name(self, name: str) -> Optional[ToolMetadata]:
        """Get tool by name (latest version)"""
        index = self._load_index()

        # Find all tools with this name
        matching = [
            ToolMetadata(**data)
            for tid, data in index.items()
            if data.get("name") == name
        ]

        if not matching:
            return None

        # Return most recently created
        return sorted(matching, key=lambda x: x.created_at, reverse=True)[0]

    def list_tools(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ToolMetadata]:
        """List tools with optional filters"""
        index = self._load_index()

        tools = [ToolMetadata(**data) for data in index.values()]

        # Apply filters
        if platform:
            tools = [t for t in tools if t.platform == platform]

        if category:
            tools = [t for t in tools if t.category == category]

        # Sort by created_at (newest first)
        tools.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        return tools[offset:offset + limit]

    def update_deployment_status(self, tool_id: str, status: str) -> bool:
        """Update deployment status of a tool"""
        index = self._load_index()

        if tool_id not in index:
            return False

        index[tool_id]["deployment_status"] = status
        index[tool_id]["updated_at"] = datetime.utcnow().isoformat()

        self._save_index(index)
        self.logger.info("Deployment status updated", tool_id=tool_id, status=status)

        return True

    def delete_tool(self, tool_id: str) -> bool:
        """Delete a tool from index"""
        index = self._load_index()

        if tool_id not in index:
            return False

        del index[tool_id]
        self._save_index(index)

        self.logger.info("Tool deleted", tool_id=tool_id)
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        index = self._load_index()

        tools = [ToolMetadata(**data) for data in index.values()]

        stats = {
            "total_tools": len(tools),
            "by_platform": {},
            "by_category": {},
            "by_status": {},
            "total_code_size": sum(t.code_size for t in tools)
        }

        for tool in tools:
            # Count by platform
            stats["by_platform"][tool.platform] = stats["by_platform"].get(tool.platform, 0) + 1

            # Count by category
            stats["by_category"][tool.category] = stats["by_category"].get(tool.category, 0) + 1

            # Count by status
            stats["by_status"][tool.status] = stats["by_status"].get(tool.status, 0) + 1

        return stats
