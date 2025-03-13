"""
Simple browser example for Minion-Manus.

This example demonstrates how to use the Minion-Manus framework to interact with a web browser.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from minion_manus import Agent
from minion_manus.tools import BrowserTool


async def main():
    """Run the example."""
    # Create an agent
    agent = Agent(name="Browser Agent")
    
    try:
        # Add a browser tool to the agent
        browser_tool = BrowserTool()
        agent.add_tool(browser_tool)
        
        # Example 1: Navigate to a website
        print("Example 1: Navigate to a website")
        result = await browser_tool.execute("navigate", url="https://www.example.com")
        print(f"Result: {result.message}")
        
        # Example 2: Get the page content
        print("\nExample 2: Get the page content")
        result = await browser_tool.execute("get_text")
        print(f"Page content: {result.data['text'][:200]}...")
        
        # Example 3: Take a screenshot
        print("\nExample 3: Take a screenshot")
        result = await browser_tool.execute("screenshot")
        print(f"Screenshot taken: {result.success}")
        
        # Example 4: Use the agent to run a task
        print("\nExample 4: Use the agent to run a task")
        result = await agent.run("Search for 'Python programming' and summarize the first result")
        print(f"Task result: {result['message']}")
        if result['data']:
            print(f"Search query: {result['data']['search_query']}")
            print(f"Search results preview: {result['data']['search_results'][:200]}...")
    
    finally:
        # Clean up resources
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 