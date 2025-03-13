"""
Browser tool for Minion-Manus.

This module provides a browser tool that can be used with the Minion-Manus framework.
It is based on the browser_use_tool from OpenManus.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union

from browser_use import Browser as BrowserUseBrowser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.dom.service import DomService
from loguru import logger
from pydantic import BaseModel, Field

MAX_LENGTH = 2000

BROWSER_DESCRIPTION = """
Interact with a web browser to perform various actions such as navigation, element interaction,
content extraction, and tab management. Supported actions include:
- 'navigate': Go to a specific URL
- 'click': Click an element by index
- 'input_text': Input text into an element
- 'screenshot': Capture a screenshot
- 'get_html': Get page HTML content
- 'get_text': Get text content of the page
- 'read_links': Get all links on the page
- 'execute_js': Execute JavaScript code
- 'scroll': Scroll the page
- 'switch_tab': Switch to a specific tab
- 'new_tab': Open a new tab
- 'close_tab': Close the current tab
- 'refresh': Refresh the current page
"""


class BrowserToolResult(BaseModel):
    """Result of a browser tool execution."""
    
    success: bool = True
    message: str = ""
    data: Optional[Any] = None


class BrowserTool:
    """Browser tool for Minion-Manus."""
    
    def __init__(self):
        """Initialize the browser tool."""
        self.name = "browser_use"
        self.description = BROWSER_DESCRIPTION
        self.lock = asyncio.Lock()
        self.browser: Optional[BrowserUseBrowser] = None
        self.context: Optional[BrowserContext] = None
        self.dom_service: Optional[DomService] = None
    
    async def _ensure_browser_initialized(self) -> BrowserContext:
        """Ensure that the browser is initialized."""
        if self.browser is None:
            logger.info("Initializing browser")
            config = BrowserConfig(headless=False)
            self.browser = BrowserUseBrowser(config)
            self.context = await self.browser.new_context()
        return self.context
    
    async def execute(
        self,
        action: str,
        url: Optional[str] = None,
        index: Optional[int] = None,
        text: Optional[str] = None,
        script: Optional[str] = None,
        scroll_amount: Optional[int] = None,
        tab_id: Optional[int] = None,
        **kwargs,
    ) -> BrowserToolResult:
        """Execute a browser action."""
        async with self.lock:
            try:
                context = await self._ensure_browser_initialized()
                
                if action == "navigate":
                    if not url:
                        return BrowserToolResult(
                            success=False, message="URL is required for navigate action"
                        )
                    await context.goto(url)
                    return BrowserToolResult(
                        success=True, message=f"Navigated to {url}"
                    )
                
                elif action == "click":
                    if index is None:
                        return BrowserToolResult(
                            success=False, message="Index is required for click action"
                        )
                    elements = await context.query_selector_all("a, button, input[type=submit], input[type=button]")
                    if index >= len(elements):
                        return BrowserToolResult(
                            success=False,
                            message=f"Index {index} is out of range. Only {len(elements)} elements found.",
                        )
                    await elements[index].click()
                    return BrowserToolResult(
                        success=True, message=f"Clicked element at index {index}"
                    )
                
                elif action == "input_text":
                    if index is None:
                        return BrowserToolResult(
                            success=False, message="Index is required for input_text action"
                        )
                    if text is None:
                        return BrowserToolResult(
                            success=False, message="Text is required for input_text action"
                        )
                    elements = await context.query_selector_all("input[type=text], textarea")
                    if index >= len(elements):
                        return BrowserToolResult(
                            success=False,
                            message=f"Index {index} is out of range. Only {len(elements)} elements found.",
                        )
                    await elements[index].fill(text)
                    return BrowserToolResult(
                        success=True, message=f"Input text '{text}' at index {index}"
                    )
                
                elif action == "screenshot":
                    screenshot = await context.screenshot()
                    return BrowserToolResult(
                        success=True,
                        message="Screenshot captured",
                        data={"screenshot": screenshot},
                    )
                
                elif action == "get_html":
                    html = await context.content()
                    if len(html) > MAX_LENGTH:
                        html = html[:MAX_LENGTH] + "... (truncated)"
                    return BrowserToolResult(
                        success=True, message="HTML content retrieved", data={"html": html}
                    )
                
                elif action == "get_text":
                    text = await context.inner_text("body")
                    if len(text) > MAX_LENGTH:
                        text = text[:MAX_LENGTH] + "... (truncated)"
                    return BrowserToolResult(
                        success=True, message="Text content retrieved", data={"text": text}
                    )
                
                elif action == "read_links":
                    elements = await context.query_selector_all("a")
                    links = []
                    for element in elements:
                        href = await element.get_attribute("href")
                        text = await element.inner_text()
                        if href:
                            links.append({"href": href, "text": text})
                    return BrowserToolResult(
                        success=True,
                        message=f"Found {len(links)} links",
                        data={"links": links},
                    )
                
                elif action == "execute_js":
                    if not script:
                        return BrowserToolResult(
                            success=False, message="Script is required for execute_js action"
                        )
                    result = await context.evaluate(script)
                    return BrowserToolResult(
                        success=True,
                        message="JavaScript executed",
                        data={"result": str(result)},
                    )
                
                elif action == "scroll":
                    if scroll_amount is None:
                        return BrowserToolResult(
                            success=False, message="Scroll amount is required for scroll action"
                        )
                    await context.evaluate(f"window.scrollBy(0, {scroll_amount})")
                    return BrowserToolResult(
                        success=True, message=f"Scrolled by {scroll_amount} pixels"
                    )
                
                elif action == "switch_tab":
                    if tab_id is None:
                        return BrowserToolResult(
                            success=False, message="Tab ID is required for switch_tab action"
                        )
                    # Implementation depends on how tabs are managed in browser-use
                    return BrowserToolResult(
                        success=False, message="Switch tab not implemented yet"
                    )
                
                elif action == "new_tab":
                    if not url:
                        return BrowserToolResult(
                            success=False, message="URL is required for new_tab action"
                        )
                    # Implementation depends on how tabs are managed in browser-use
                    new_context = await self.browser.new_context()
                    await new_context.goto(url)
                    return BrowserToolResult(
                        success=True, message=f"Opened new tab with URL {url}"
                    )
                
                elif action == "close_tab":
                    # Implementation depends on how tabs are managed in browser-use
                    return BrowserToolResult(
                        success=False, message="Close tab not implemented yet"
                    )
                
                elif action == "refresh":
                    await context.reload()
                    return BrowserToolResult(
                        success=True, message="Page refreshed"
                    )
                
                else:
                    return BrowserToolResult(
                        success=False, message=f"Unknown action: {action}"
                    )
            
            except Exception as e:
                logger.exception(f"Error executing browser action: {e}")
                return BrowserToolResult(
                    success=False, message=f"Error: {str(e)}"
                )
    
    async def get_current_state(self) -> BrowserToolResult:
        """Get the current state of the browser."""
        async with self.lock:
            try:
                if self.context is None:
                    return BrowserToolResult(
                        success=False, message="Browser not initialized"
                    )
                
                url = await self.context.url()
                title = await self.context.title()
                
                return BrowserToolResult(
                    success=True,
                    message="Current browser state retrieved",
                    data={"url": url, "title": title},
                )
            
            except Exception as e:
                logger.exception(f"Error getting browser state: {e}")
                return BrowserToolResult(
                    success=False, message=f"Error: {str(e)}"
                )
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.browser:
            try:
                await self.browser.close()
                self.browser = None
                self.context = None
                self.dom_service = None
                logger.info("Browser closed")
            except Exception as e:
                logger.exception(f"Error closing browser: {e}")
    
    def __del__(self):
        """Destructor to ensure browser is closed."""
        if self.browser:
            logger.warning("Browser was not properly closed. Forcing cleanup.")
            asyncio.create_task(self.cleanup()) 