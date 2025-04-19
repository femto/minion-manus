"""
Logging utilities for Minion-Manus.

This module provides utilities for setting up logging.
"""

import sys
from typing import Optional

from loguru import logger

from minion_manus.config import Settings


def setup_logging(settings: Optional[Settings] = None) -> None:
    """Set up logging.
    
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