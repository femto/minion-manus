"""
Settings module for Minion-Manus.

This module provides a Settings class for managing configuration settings.
"""

import os
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict, Field
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

__all__ = ['AgentFramework', 'MCPTool', 'AgentConfig', 'Settings', 'settings']


class AgentFramework(str, Enum):
    GOOGLE = "google"
    LANGCHAIN = "langchain"
    LLAMAINDEX = "llama_index"
    OPENAI = "openai"
    SMOLAGENTS = "smolagents"


class MCPTool(BaseModel):
    command: str
    args: list[str]
    tools: list[str] | None = None

class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model_id: str
    name: str = "Minion-Manus"
    instructions: str | None = None
    tools: list[str | MCPTool] = Field(default_factory=list)
    handoff: bool = False
    agent_type: str | None = None
    agent_args: dict | None = None
    model_type: str | None = None
    model_args: dict | None = None
    description: str | None = None


class BrowserSettings(BaseModel):
    """Browser settings."""
    
    headless: bool = Field(
        default=os.getenv("MINION_MANUS_BROWSER_HEADLESS", "False").lower() == "true",
        description="Whether to run the browser in headless mode.",
    )
    width: int = Field(
        default=int(os.getenv("MINION_MANUS_BROWSER_WIDTH", "1280")),
        description="Browser window width.",
    )
    height: int = Field(
        default=int(os.getenv("MINION_MANUS_BROWSER_HEIGHT", "800")),
        description="Browser window height.",
    )
    user_agent: Optional[str] = Field(
        default=os.getenv("MINION_MANUS_BROWSER_USER_AGENT"),
        description="Browser user agent.",
    )
    timeout: int = Field(
        default=int(os.getenv("MINION_MANUS_BROWSER_TIMEOUT", "30000")),
        description="Browser timeout in milliseconds.",
    )


class LoggingSettings(BaseModel):
    """Logging settings."""
    
    level: str = Field(
        default=os.getenv("MINION_MANUS_LOG_LEVEL", "INFO"),
        description="Logging level.",
    )
    format: str = Field(
        default=os.getenv(
            "MINION_MANUS_LOG_FORMAT",
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        ),
        description="Logging format.",
    )
    file: Optional[str] = Field(
        default=os.getenv("MINION_MANUS_LOG_FILE"),
        description="Log file path.",
    )


class Settings(BaseModel):
    """Settings for Minion-Manus."""
    
    browser: BrowserSettings = Field(
        default_factory=BrowserSettings,
        description="Browser settings.",
    )
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging settings.",
    )
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        return cls()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """Create settings from a dictionary."""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to a dictionary."""
        return self.model_dump()


# Global settings instance
settings = Settings.from_env() 