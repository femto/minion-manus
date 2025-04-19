"""Minion Manus - A wrapper for smolagents."""

__version__ = "0.1.0"

from .frameworks.smolagents import MinionAgent
from .config import AgentConfig

__all__ = ["MinionAgent", "AgentConfig"] 