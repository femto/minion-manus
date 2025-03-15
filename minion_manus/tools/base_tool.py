import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @abstractmethod
    def _execute(self, **kwargs) -> Any:
        """Tool implementation - can be sync or async."""
        pass

    def execute(self, **kwargs) -> Any:
        """
        Universal execute method that handles both sync and async implementations.
        Returns result directly for sync tools, and a coroutine for async tools.
        """
        return self._execute(**kwargs)

    async def aexecute(self, **kwargs) -> Any:
        """
        Ensures async execution regardless of implementation.
        """
        result = self._execute(**kwargs)
        if inspect.isawaitable(result):
            return await result
        return result





