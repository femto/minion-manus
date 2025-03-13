"""
Agent module for Minion-Manus.

This module provides the Agent class that serves as the main interface for the framework.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union

from loguru import logger


class Agent:
    """Agent class for Minion-Manus."""
    
    def __init__(self, name: str = "Minion-Manus Agent"):
        """Initialize the agent.
        
        Args:
            name: The name of the agent.
        """
        self.name = name
        self.tools = {}
        logger.info(f"Agent '{name}' initialized")
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent.
        
        Args:
            tool: The tool to add.
        """
        self.tools[tool.name] = tool
        logger.info(f"Tool '{tool.name}' added to agent '{self.name}'")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name.
        
        Args:
            name: The name of the tool.
            
        Returns:
            The tool if found, None otherwise.
        """
        return self.tools.get(name)
    
    async def run(self, task: str) -> Dict[str, Any]:
        """Run a task with the agent.
        
        Args:
            task: The task to run.
            
        Returns:
            The result of the task.
        """
        logger.info(f"Running task: {task}")
        
        # This is a placeholder for the actual implementation
        # In a real implementation, this would parse the task, determine which tools to use,
        # and execute the appropriate actions
        
        result = {
            "success": True,
            "message": f"Task '{task}' completed",
            "data": None
        }
        
        # Example of using the browser tool if available
        browser_tool = self.get_tool("browser_use")
        if browser_tool and "search" in task.lower():
            # Extract search query from task (simplified)
            search_query = task.split("'")[1] if "'" in task else task
            
            try:
                # Navigate directly to Google search results
                search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                await browser_tool.execute("navigate", url=search_url)
                
                # Wait for results to load
                await asyncio.sleep(2)
                
                # Get the search results
                text_result = await browser_tool.execute("get_text")
                
                result["data"] = {
                    "search_query": search_query,
                    "search_results": text_result.data["text"] if text_result.success else "Failed to get results"
                }
            except Exception as e:
                logger.exception(f"Error executing search: {e}")
                result["data"] = {
                    "search_query": search_query,
                    "search_results": f"Error: {str(e)}"
                }
        
        return result
    
    async def cleanup(self) -> None:
        """Clean up resources used by the agent."""
        logger.info(f"Cleaning up agent '{self.name}'")
        
        for tool_name, tool in self.tools.items():
            if hasattr(tool, "cleanup") and callable(tool.cleanup):
                try:
                    await tool.cleanup()
                    logger.info(f"Tool '{tool_name}' cleaned up")
                except Exception as e:
                    logger.exception(f"Error cleaning up tool '{tool_name}': {e}")
    
    async def __aenter__(self):
        """Enter the context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        await self.cleanup() 