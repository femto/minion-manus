"""
Settings module for Minion-Manus.

This module provides a Settings class for managing configuration settings.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load environment variables from .env file
load_dotenv()


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