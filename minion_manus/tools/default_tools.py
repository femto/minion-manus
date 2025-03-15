# Configure logging for search tool
import logging

from minion_manus.tools.base_tool import BaseTool

logger = logging.getLogger("search_tool")


class DuckDuckGoSearchTool(BaseTool):
    name = "web_search"
    description = "Performs a duckduckgo web search based on your query (think a Google search) then returns the top search results."

    def __init__(self, max_results: int = 10, **kwargs):
        """Initialize the DuckDuckGoSearchTool.

        Args:
            max_results: Maximum number of search results to return. Defaults to 10.
            **kwargs: Additional arguments to pass to the DDGS constructor.
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise ImportError(
                "You must install package `duckduckgo_search` to run this tool: for instance run `pip install duckduckgo-search`."
            ) from e

        self.max_results = max_results
        self.ddgs = DDGS(**kwargs)

    def _execute(self, query: str) -> str:
        """Execute the search tool.

        Args:
            query: The search query to perform.

        Returns:
            A formatted string containing the search results.
        """
        try:
            results = self.ddgs.text(query, max_results=self.max_results)

            if len(results) == 0:
                return "No results found! Try a less restrictive/shorter query."

            postprocessed_results = [
                f"[{result['title']}]({result['href']})\n{result['body']}"
                for result in results
            ]

            return "## Search Results\n\n" + "\n\n".join(postprocessed_results)
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return f"Error during search: {str(e)}"


class AsyncDuckDuckGoSearchTool(BaseTool):
    name = "async_web_search"
    description = "Performs an asynchronous duckduckgo web search based on your query and returns the top search results."

    def __init__(self, max_results: int = 10, **kwargs):
        """Initialize the AsyncDuckDuckGoSearchTool.

        Args:
            max_results: Maximum number of search results to return. Defaults to 10.
            **kwargs: Additional arguments to pass to the DDGS constructor.
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise ImportError(
                "You must install package `duckduckgo_search` to run this tool: for instance run `pip install duckduckgo-search`."
            ) from e

        self.max_results = max_results
        self.ddgs = DDGS(**kwargs)

    async def _execute(self, query: str) -> str:
        """Execute the search tool asynchronously.

        Args:
            query: The search query to perform.

        Returns:
            A formatted string containing the search results.
        """
        try:
            # Note: DDGS.text is not async, but we can wrap it in an async function
            # In a real implementation, you might want to use asyncio.to_thread for Python 3.9+
            results = self.ddgs.text(query, max_results=self.max_results)

            if len(results) == 0:
                return "No results found! Try a less restrictive/shorter query."

            postprocessed_results = [
                f"[{result['title']}]({result['href']})\n{result['body']}"
                for result in results
            ]

            return "## Search Results\n\n" + "\n\n".join(postprocessed_results)
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return f"Error during search: {str(e)}"