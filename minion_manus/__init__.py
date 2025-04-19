"""Minion Manus - A wrapper for smolagents."""

__version__ = "0.1.0"


from .config import AgentConfig, AgentFramework
from .frameworks.minion_agent import MinionAgent

__all__ = ["MinionAgent", "AgentConfig", "AgentFramework"]
