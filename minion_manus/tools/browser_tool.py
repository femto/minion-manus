"""
Browser tool for Minion-Manus.

This module provides browser functionality that can be used with the Minion-Manus framework.
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

from smolagents import tool

MAX_LENGTH = 2000

# Valid browser actions
VALID_ACTIONS = {
    "navigate", "click", "input_text", "screenshot", "get_html",
    "get_text", "read_links", "execute_js", "scroll", "switch_tab",
    "new_tab", "close_tab", "refresh"
}

class BrowserToolResult(BaseModel):
    """Result of a browser tool execution."""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None

_browser: Optional[BrowserUseBrowser] = None
_context: Optional[BrowserContext] = None
_lock = asyncio.Lock()

async def _ensure_browser_initialized() -> BrowserContext:
    """Ensure that the browser is initialized."""
    global _browser, _context
    if _browser is None:
        logger.info("Initializing browser")
        config = BrowserConfig(headless=False)
        _browser = BrowserUseBrowser(config)
        _context = await _browser.new_context()
    return _context

def run_async(coro):
    """Run an async coroutine to completion and return its result."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

#@tool
def browser(
    action: str,
    url: Optional[str] = None,
    index: Optional[int] = None,
    text: Optional[str] = None,
    script: Optional[str] = None,
    scroll_amount: Optional[int] = None,
    tab_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute browser actions to interact with web pages.

    This function provides various browser operations including navigation, element interaction,
    content extraction, and tab management.

    Args:
        action: The browser action to perform. Must be one of:
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
        url: URL for navigation actions
        index: Element index for click/input actions
        text: Text for input actions
        script: JavaScript code to execute
        scroll_amount: Amount to scroll in pixels
        tab_id: Tab ID for tab management actions

    Returns:
        Dict containing:
            - success: Whether the action was successful
            - message: Description of what happened
            - data: Optional data returned by the action
    """
    return run_async(_async_browser(
        action=action,
        url=url,
        index=index,
        text=text,
        script=script,
        scroll_amount=scroll_amount,
        tab_id=tab_id
    ))

async def _async_browser(
    action: str,
    url: Optional[str] = None,
    index: Optional[int] = None,
    text: Optional[str] = None,
    script: Optional[str] = None,
    scroll_amount: Optional[int] = None,
    tab_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute browser actions to interact with web pages.

    This function provides various browser operations including navigation, element interaction,
    content extraction, and tab management.

    Args:
        action: The browser action to perform. Must be one of:
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
        url: URL for navigation actions
        index: Element index for click/input actions
        text: Text for input actions
        script: JavaScript code to execute
        scroll_amount: Amount to scroll in pixels
        tab_id: Tab ID for tab management actions

    Returns:
        Dict containing:
            - success: Whether the action was successful
            - message: Description of what happened
            - data: Optional data returned by the action
    """
    async with _lock:
        try:
            if action not in VALID_ACTIONS:
                return BrowserToolResult(
                    success=False,
                    message=f"Invalid action: {action}. Must be one of: {', '.join(sorted(VALID_ACTIONS))}"
                ).dict()

            context = await _ensure_browser_initialized()
            result = BrowserToolResult()

            if action == "navigate":
                if not url:
                    result.success = False
                    result.message = "URL is required for navigate action"
                else:
                    page = await context.get_current_page()
                    await page.goto(url)
                    result.message = f"Navigated to {url}"

            elif action == "click":
                if index is None:
                    result.success = False
                    result.message = "Index is required for click action"
                else:
                    element = await context.get_dom_element_by_index(index)
                    if not element:
                        result.success = False
                        result.message = f"Element with index {index} not found"
                    else:
                        await context._click_element_node(element)
                        result.message = f"Clicked element at index {index}"

            elif action == "input_text":
                if index is None:
                    result.success = False
                    result.message = "Index is required for input_text action"
                elif text is None:
                    result.success = False
                    result.message = "Text is required for input_text action"
                else:
                    element = await context.get_dom_element_by_index(index)
                    if not element:
                        result.success = False
                        result.message = f"Element with index {index} not found"
                    else:
                        await context._input_text_element_node(element, text)
                        result.message = f"Input text '{text}' at index {index}"

            elif action == "screenshot":
                page = await context.get_current_page()
                screenshot = await page.screenshot()
                result.message = "Screenshot captured"
                result.data = {"screenshot": screenshot}

            elif action == "get_html":
                page = await context.get_current_page()
                html = await page.content()
                if len(html) > MAX_LENGTH:
                    html = html[:MAX_LENGTH] + "... (truncated)"
                result.message = "HTML content retrieved"
                result.data = {"html": html}

            elif action == "get_text":
                page = await context.get_current_page()
                text = await page.inner_text("body")
                if len(text) > MAX_LENGTH:
                    text = text[:MAX_LENGTH] + "... (truncated)"
                result.message = "Text content retrieved"
                result.data = {"text": text}

            elif action == "read_links":
                page = await context.get_current_page()
                elements = await page.query_selector_all("a")
                links = []
                for element in elements:
                    href = await element.get_attribute("href")
                    text = await element.inner_text()
                    if href:
                        links.append({"href": href, "text": text})
                result.message = f"Found {len(links)} links"
                result.data = {"links": links}

            elif action == "execute_js":
                if not script:
                    result.success = False
                    result.message = "Script is required for execute_js action"
                else:
                    page = await context.get_current_page()
                    js_result = await page.evaluate(script)
                    result.message = "JavaScript executed"
                    result.data = {"result": str(js_result)}

            elif action == "scroll":
                if scroll_amount is None:
                    result.success = False
                    result.message = "Scroll amount is required for scroll action"
                else:
                    page = await context.get_current_page()
                    await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                    result.message = f"Scrolled by {scroll_amount} pixels"

            elif action == "switch_tab":
                if tab_id is None:
                    result.success = False
                    result.message = "Tab ID is required for switch_tab action"
                else:
                    await context.switch_to_tab(tab_id)
                    result.message = f"Switched to tab {tab_id}"

            elif action == "new_tab":
                if not url:
                    result.success = False
                    result.message = "URL is required for new_tab action"
                else:
                    await context.create_new_tab(url)
                    result.message = f"Opened new tab with URL {url}"

            elif action == "close_tab":
                await context.close_current_tab()
                result.message = "Closed current tab"

            elif action == "refresh":
                page = await context.get_current_page()
                await page.reload()
                result.message = "Page refreshed"
            
            return result.dict()
        
        except Exception as e:
            logger.exception(f"Error executing browser action: {e}")
            return BrowserToolResult(
                success=False,
                message=f"Error: {str(e)}"
            ).dict()

async def cleanup() -> None:
    """Clean up browser resources."""
    global _browser, _context
    if _browser:
        try:
            await _browser.close()
            _browser = None
            _context = None
            logger.info("Browser closed")
        except Exception as e:
            logger.exception(f"Error closing browser: {e}")

async def get_current_state() -> Dict[str, Any]:
    """Get the current state of the browser.
    
    Returns:
        Dict containing the current URL and page title.
    """
    async with _lock:
        try:
            if _context is None:
                return BrowserToolResult(
                    success=False,
                    message="Browser not initialized"
                ).dict()
            
            state = await _context.get_state()
            
            return BrowserToolResult(
                success=True,
                message="Current browser state retrieved",
                data={"url": state.url, "title": state.title},
            ).dict()
        
        except Exception as e:
            logger.exception(f"Error getting browser state: {e}")
            return BrowserToolResult(
                success=False,
                message=f"Error: {str(e)}"
            ).dict() 