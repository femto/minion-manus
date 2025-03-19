"""
Logging utilities for Minion-Manus.

This module provides utilities for setting up logging.
"""

import sys
from typing import Optional
from datetime import datetime
from pathlib import Path

from loguru import logger

from minion_manus.config import Settings

# Global logger instance that can be imported
_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to the specified levels
    
    Args:
        print_level (str): Log level for console output
        logfile_level (str): Log level for file output
        name (str, optional): Prefix for the log filename
        
    Returns:
        logger: Configured logger instance
    """
    global _print_level
    _print_level = print_level

    # Setup log file name with date prefix
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    log_name = f"{name}_{formatted_date}" if name else formatted_date
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure loggers
    logger.remove()
    logger.add(
        sys.stderr,
        level=print_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.add(
        log_dir / f"{log_name}.txt", 
        level=logfile_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        rotation="10 MB",
        compression="zip",
    )
    
    logger.info(f"{name} logging setup complete with level {print_level}")
    return logger


def setup_logging(settings: Optional[Settings] = None) -> None:
    """Set up logging based on settings.
    
    Args:
        settings: Settings for logging. If None, the default settings will be used.
    """
    settings = settings or Settings.from_env()
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        level=settings.logging.level,
        format=settings.logging.format,
        colorize=True,
    )
    
    # Add file logger if configured
    if settings.logging.file:
        logger.add(
            settings.logging.file,
            level=settings.logging.level,
            format=settings.logging.format,
            rotation="10 MB",
            compression="zip",
        )
    
    logger.info("Logging configured")


# Functions for handling LLM streaming logs
def log_llm_stream(msg):
    """Log LLM streaming output."""
    _llm_stream_log(msg)


def set_llm_stream_logfunc(func):
    """Set a custom function for logging LLM streaming output."""
    global _llm_stream_log
    _llm_stream_log = func


def _llm_stream_log(msg):
    """Default function for logging LLM streaming output."""
    if _print_level in ["INFO", "DEBUG"]:
        print(msg, end="") 