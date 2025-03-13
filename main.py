"""
Main entry point for Minion-Manus.

This module provides a simple entry point for the Minion-Manus framework.
"""

import asyncio
import argparse
import sys
from typing import List, Optional

from loguru import logger

from minion_manus import Agent
from minion_manus.config import Settings
from minion_manus.tools import BrowserTool
from minion_manus.utils import setup_logging


async def run_task(task: str, headless: bool = False) -> None:
    """Run a task with an agent.
    
    Args:
        task: The task to run.
        headless: Whether to run the browser in headless mode.
    """
    # Load settings
    settings = Settings.from_env()
    
    # Override headless setting if specified
    if headless:
        settings.browser.headless = True
    
    # Set up logging
    setup_logging(settings)
    
    # Create an agent
    agent = Agent(name="Minion-Manus Agent")
    
    try:
        # Add a browser tool to the agent
        browser_tool = BrowserTool(settings=settings)
        agent.add_tool(browser_tool)
        
        # Run the task
        logger.info(f"Running task: {task}")
        result = await agent.run(task)
        
        # Print the result
        if result["success"]:
            logger.info(f"Task completed: {result['message']}")
            if result["data"]:
                logger.info(f"Result data: {result['data']}")
        else:
            logger.error(f"Task failed: {result['message']}")
    
    finally:
        # Clean up resources
        await agent.cleanup()


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.
    
    Args:
        args: Command line arguments. If None, sys.argv[1:] will be used.
        
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Minion-Manus: A framework combining Minion with browser use capabilities")
    parser.add_argument("task", help="The task to run")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode")
    
    return parser.parse_args(args)


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code.
    """
    args = parse_args()
    
    try:
        asyncio.run(run_task(args.task, args.headless))
        return 0
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 