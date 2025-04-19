"""Configuration classes for Minion Manus."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class AgentConfig:
    """Configuration for a Minion Manus agent."""

    model_id: str
    name: str = "Minion"
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: List[str] = field(default_factory=list)
    model_args: Optional[Dict[str, Any]] = None
    agent_args: Optional[Dict[str, Any]] = None 