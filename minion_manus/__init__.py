"""
Minion-Manus: A toolkit for implementing and managing tools for LLM agents.

This package provides a standardized way to create, execute, and validate tools
that can be used with various LLM frameworks and agent architectures.
"""

__version__ = "0.1.0"

# Import submodules
from minion_manus import tools
from minion_manus import providers

__all__ = [
    "tools",
    "providers",
]
