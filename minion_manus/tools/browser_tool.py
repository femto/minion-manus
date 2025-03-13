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

from minion_manus.config import Settings

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
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the browser tool.
        
        Args:
            settings: Optional settings for the browser tool.
        """
        self.name = "browser_use"
        self.description = BROWSER_DESCRIPTION
        self.lock = asyncio.Lock()
        self.browser: Optional[BrowserUseBrowser] = None
        self.context: Optional[BrowserContext] = None
        self.page = None
        self.dom_service: Optional[DomService] = None
        self.settings = settings
    
    async def _ensure_browser_initialized(self) -> BrowserContext:
        """Ensure that the browser is initialized."""
        if self.browser is None:
            logger.info("Initializing browser")
            if self.settings and self.settings.browser:
                config = BrowserConfig(headless=self.settings.browser.headless)
            else:
                config = BrowserConfig(headless=False)
            self.browser = BrowserUseBrowser(config)
            self.context = await self.browser.new_context()
            # The context is the page in browser_use
            self.page = self.context
        return self.page
    
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
                page_context = await self._ensure_browser_initialized()
                
                if action == "navigate":
                    if not url:
                        return BrowserToolResult(
                            success=False, message="URL is required for navigate action"
                        )
                    await page_context.navigate_to(url)
                    return BrowserToolResult(
                        success=True, message=f"Navigated to {url}"
                    )
                
                elif action == "click":
                    if index is None:
                        return BrowserToolResult(
                            success=False, message="Index is required for click action"
                        )
                    try:
                        # Get the DOM element by index and click it
                        element_node = await page_context.get_dom_element_by_index(index)
                        await page_context._click_element_node(element_node)
                        return BrowserToolResult(
                            success=True, message=f"Clicked element at index {index}"
                        )
                    except KeyError:
                        return BrowserToolResult(
                            success=False, message=f"Element with index {index} not found"
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
                    try:
                        # Get the DOM element by index and input text
                        element_node = await page_context.get_dom_element_by_index(index)
                        await page_context._input_text_element_node(element_node, text)
                        return BrowserToolResult(
                            success=True, message=f"Input text '{text}' at index {index}"
                        )
                    except KeyError:
                        return BrowserToolResult(
                            success=False, message=f"Element with index {index} not found"
                        )
                
                elif action == "screenshot":
                    screenshot = await page_context.take_screenshot(full_page=kwargs.get("full_page", False))
                    return BrowserToolResult(
                        success=True,
                        message="Screenshot captured",
                        data={"screenshot": screenshot},
                    )
                
                elif action == "get_html":
                    # Get the HTML content
                    current_page = await page_context.get_current_page()
                    html = await current_page.content()
                    if len(html) > MAX_LENGTH:
                        html = html[:MAX_LENGTH] + "... (truncated)"
                    return BrowserToolResult(
                        success=True, message="HTML content retrieved", data={"html": html}
                    )
                
                elif action == "get_text":
                    # Get the text content
                    current_page = await page_context.get_current_page()
                    text = await current_page.evaluate("document.body.innerText")
                    if len(text) > MAX_LENGTH:
                        text = text[:MAX_LENGTH] + "... (truncated)"
                    return BrowserToolResult(
                        success=True, message="Text content retrieved", data={"text": text}
                    )
                
                elif action == "read_links":
                    # Get all links
                    current_page = await page_context.get_current_page()
                    links_data = await current_page.evaluate("""
                        () => {
                            const links = [];
                            document.querySelectorAll('a').forEach(a => {
                                links.push({
                                    href: a.href,
                                    text: a.innerText.trim()
                                });
                            });
                            return links;
                        }
                    """)
                    return BrowserToolResult(
                        success=True,
                        message=f"Found {len(links_data)} links",
                        data={"links": links_data},
                    )
                
                elif action == "execute_js":
                    if not script:
                        return BrowserToolResult(
                            success=False, message="Script is required for execute_js action"
                        )
                    # Execute JavaScript
                    current_page = await page_context.get_current_page()
                    result = await current_page.evaluate(script)
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
                    # Scroll
                    current_page = await page_context.get_current_page()
                    await current_page.evaluate(f"window.scrollBy(0, {scroll_amount})")
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
                    await page_context.create_new_tab(url)
                    return BrowserToolResult(
                        success=True, message=f"Opened new tab with URL {url}"
                    )
                
                elif action == "close_tab":
                    # Implementation depends on how tabs are managed in browser-use
                    return BrowserToolResult(
                        success=False, message="Close tab not implemented yet"
                    )
                
                elif action == "refresh":
                    # Refresh
                    current_page = await page_context.get_current_page()
                    await current_page.reload()
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
                if self.page is None:
                    return BrowserToolResult(
                        success=False, message="Browser not initialized"
                    )
                
                # Get the current page
                current_page = await self.page.get_current_page()
                
                # Get the URL and title
                url = await current_page.evaluate("window.location.href")
                title = await current_page.evaluate("document.title")
                
                return BrowserToolResult(
                    success=True,
                    message="Current browser state retrieved",
                    data={
                        "url": url,
                        "title": title,
                    },
                )
            except Exception as e:
                logger.exception(f"Error getting browser state: {e}")
                return BrowserToolResult(
                    success=False, message=f"Error: {str(e)}"
                )
    
    async def cleanup(self):
        """Clean up resources."""
        async with self.lock:
            if self.browser:
                logger.info("Browser closed")
                await self.browser.close()
                self.browser = None
                self.context = None
                self.page = None
    
    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        if hasattr(self, 'browser') and self.browser:
            asyncio.create_task(self.cleanup()) 