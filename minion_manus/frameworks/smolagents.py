"""Smolagents wrapper implementation."""

import os
from typing import Optional, Any, List

try:
    import smolagents
    from smolagents import MultiStepAgent
    smolagents_available = True
except ImportError:
    smolagents_available = False

from ..config import AgentConfig, AgentFramework
from ..tools.wrappers import import_and_wrap_tools

DEFAULT_AGENT_TYPE = "CodeAgent"
DEFAULT_MODEL_CLASS = "LiteLLMModel"


class MinionAgent:
    """Smolagents agent implementation with simplified interface."""

    def __init__(self, config: AgentConfig):
        if not smolagents_available:
            raise ImportError(
                "You need to install smolagents to use this agent. Try: pip install smolagents"
            )
        self.config = config
        self._agent = None
        self._mcp_servers = None

    def _get_model(self):
        """Get the model configuration for the agent."""
        model_type = getattr(smolagents, DEFAULT_MODEL_CLASS)
        kwargs = {
            "model_id": self.config.model_id,
        }
        model_args = self.config.model_args or {}
        if api_key_var := model_args.pop("api_key_var", None):
            kwargs["api_key"] = os.environ[api_key_var]
        return model_type(**kwargs, **model_args)

    def _merge_mcp_tools(self, mcp_servers):
        """Merge MCP tools from different servers."""
        tools = []
        for mcp_server in mcp_servers:
            tools.extend(mcp_server.tools)
        return tools

    async def _load_agent(self) -> None:
        """Load the Smolagents agent with the given configuration."""
        agent_type = getattr(smolagents, DEFAULT_AGENT_TYPE)

        # If no tools specified, use default web tools
        if not self.config.tools:
            self.config.tools = [
                "minion_manus.tools.search_web",
                "minion_manus.tools.visit_webpage",
            ]
        
        tools, mcp_servers = await import_and_wrap_tools(
            self.config.tools, 
            agent_framework=AgentFramework.SMOLAGENTS
        )
        self._mcp_servers = mcp_servers
        tools.extend(self._merge_mcp_tools(mcp_servers))

        self._agent = agent_type(
            name=self.config.name,
            model=self._get_model(),
            tools=tools,
            verbosity_level=-1,  # OFF
            **self.config.agent_args or {},
        )

        if self.config.instructions:
            self._agent.prompt_templates["system_prompt"] = self.config.instructions

    async def run(self, prompt: str) -> Any:
        """Run the agent with the given prompt."""
        if self._agent is None:
            await self._load_agent()
        return self._agent.run(prompt)

    @property
    def tools(self) -> List[str]:
        """Return the tools used by the agent."""
        return self._agent.tools if self._agent else [] 