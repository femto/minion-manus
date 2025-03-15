"""
Web scraper example for Minion-Manus.

This example demonstrates how to use the Minion-Manus framework to scrape data from a website.
"""

import asyncio
import json
import sys
import os
import ast
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from minion_manus import Agent
from minion_manus.tools import BrowserTool


async def scrape_hacker_news(browser_tool: BrowserTool) -> List[Dict[str, Any]]:
    """Scrape the top stories from Hacker News.
    
    Args:
        browser_tool: The browser tool to use.
        
    Returns:
        A list of stories, each with a title, URL, and score.
    """
    # Navigate to Hacker News
    result = await browser_tool.execute("navigate", url="https://news.ycombinator.com/")
    print(f"Navigation result: {result.message}")
    
    # Get the HTML content to debug
    html_result = await browser_tool.execute("get_html")
    if html_result.success:
        print(f"HTML content length: {len(html_result.data['html'])}")
    else:
        print(f"Failed to get HTML: {html_result.message}")
    
    # Get all the story elements using JavaScript
    script = """
    () => {
        const stories = [];
        const rows = document.querySelectorAll('tr.athing');
        
        console.log('Found ' + rows.length + ' rows');
        
        for (let i = 0; i < Math.min(rows.length, 10); i++) {
            const row = rows[i];
            const id = row.getAttribute('id');
            const titleElement = row.querySelector('td.title > span.titleline > a');
            const title = titleElement ? titleElement.textContent : '';
            const url = titleElement ? titleElement.getAttribute('href') : '';
            
            // Get the score from the next row
            const scoreRow = row.nextElementSibling;
            const scoreElement = scoreRow ? scoreRow.querySelector('span.score') : null;
            const score = scoreElement ? scoreElement.textContent : '0 points';
            
            stories.push({
                id,
                title,
                url,
                score
            });
        }
        
        return stories;
    }
    """
    
    result = await browser_tool.execute("execute_js", script=script)
    
    if not result.success:
        print(f"JavaScript execution failed: {result.message}")
        return []
    
    # Parse the result
    try:
        print(f"JavaScript result: {result.data['result']}")
        # Use ast.literal_eval instead of json.loads to handle the JavaScript object format
        stories = ast.literal_eval(result.data["result"])
        return stories
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing result: {e}")
        return []


async def main():
    """Run the example."""
    # Create an agent
    agent = Agent(name="Web Scraper Agent")
    
    try:
        # Add a browser tool to the agent
        browser_tool = BrowserTool()
        agent.add_tool(browser_tool)
        
        print("Scraping Hacker News top stories...")
        stories = await scrape_hacker_news(browser_tool)
        
        if stories:
            print(f"\nFound {len(stories)} stories:")
            for i, story in enumerate(stories, 1):
                print(f"{i}. {story['title']} ({story['score']})")
                print(f"   URL: {story['url']}")
                print()
        else:
            print("No stories found.")
        
        # Take a screenshot of the page
        print("Taking a screenshot...")
        await browser_tool.execute("screenshot")
        print("Screenshot taken.")
    
    finally:
        # Clean up resources
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 