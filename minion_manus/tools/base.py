"""Base tool implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Base class for all tools."""

    name: str
    description: str
    inputs: Dict[str, Dict[str, Any]]

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with the given arguments."""
        pass

    def to_smolagents(self):
        """Convert to smolagents tool."""
        from smolagents import Tool

        class WrappedTool(Tool):
            name = self.name
            description = self.description
            inputs = self.inputs

            async def execute(self, **kwargs):
                return await self.execute(**kwargs)

        return WrappedTool() 