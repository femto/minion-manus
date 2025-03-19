from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
import logging
import json

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    """
    Base class for tool adapters.
    
    Tool adapters convert between Minion-Manus tools and other ecosystem formats.
    They enable interoperability with various agent frameworks and libraries.
    """
    
    @abstractmethod
    def to_external(self, tool: Any) -> Any:
        """
        Convert a Minion-Manus tool to an external format.
        
        Args:
            tool: The Minion-Manus tool to convert
            
        Returns:
            The converted tool in the external format
        """
        pass
    
    @abstractmethod
    def from_external(self, external_tool: Any) -> Any:
        """
        Convert an external tool to a Minion-Manus tool.
        
        Args:
            external_tool: The external tool to convert
            
        Returns:
            The converted Minion-Manus tool
        """
        pass
    
    @abstractmethod
    def batch_to_external(self, tools: List[Any]) -> List[Any]:
        """
        Convert multiple Minion-Manus tools to external format.
        
        Args:
            tools: The Minion-Manus tools to convert
            
        Returns:
            The converted tools in the external format
        """
        pass
    
    @abstractmethod
    def batch_from_external(self, external_tools: List[Any]) -> List[Any]:
        """
        Convert multiple external tools to Minion-Manus tools.
        
        Args:
            external_tools: The external tools to convert
            
        Returns:
            The converted Minion-Manus tools
        """
        pass


class SmolaAgentsAdapter(BaseAdapter):
    """
    Adapter for SmolaAgents tools.
    
    Converts between Minion-Manus tools and SmolaAgents tools.
    """
    
    def to_external(self, tool: Any) -> Any:
        """
        Convert a Minion-Manus tool to a SmolaAgents tool.
        
        Args:
            tool: The Minion-Manus tool to convert
            
        Returns:
            The converted SmolaAgents tool
        """
        try:
            from smolagents.tools import Tool as SmolaAgentsTool
        except ImportError:
            raise ImportError("SmolaAgents is required for this adapter. Install with `pip install smolagents`.")
        
        # Create a wrapper class for the Minion-Manus tool
        class SmolaAgentsToolWrapper(SmolaAgentsTool):
            name = tool.name
            description = tool.description
            
            # Convert inputs format
            inputs = {}
            for name, details in tool.inputs.items():
                inputs[name] = {
                    "type": details["type"],
                    "description": details["description"]
                }
                if details.get("nullable", False):
                    inputs[name]["nullable"] = True
            
            output_type = tool.output_type
            skip_forward_signature_validation = True
            
            def __init__(self):
                super().__init__()
                self.minion_tool = tool
            
            def forward(self, *args, **kwargs):
                # Call the Minion-Manus tool
                return self.minion_tool(*args, **kwargs)
        
        # Return an instance of the wrapper
        return SmolaAgentsToolWrapper()
    
    def from_external(self, external_tool: Any) -> Any:
        """
        Convert a SmolaAgents tool to a Minion-Manus tool.
        
        Args:
            external_tool: The SmolaAgents tool to convert
            
        Returns:
            The converted Minion-Manus tool
        """
        try:
            from smolagents.tools import Tool as SmolaAgentsTool
            from minion_manus.tools.tool import Tool
        except ImportError as e:
            if "smolagents" in str(e):
                raise ImportError("SmolaAgents is required for this adapter. Install with `pip install smolagents`.")
            raise ImportError("Minion-Manus Tool classes are required")
        
        if not isinstance(external_tool, SmolaAgentsTool):
            raise TypeError(f"Expected SmolaAgentsTool, got {type(external_tool)}")
        
        # Create a wrapper class for the SmolaAgents tool
        class MinionToolWrapper(Tool):
            name = external_tool.name
            description = external_tool.description
            
            # Convert inputs format
            inputs = {}
            for name, details in external_tool.inputs.items():
                inputs[name] = {
                    "type": details["type"],
                    "description": details.get("description", "")
                }
                if details.get("nullable", False):
                    inputs[name]["nullable"] = True
            
            output_type = getattr(external_tool, "output_type", "any")
            
            def forward(self, *args, **kwargs):
                # Call the SmolaAgents tool
                return external_tool(*args, **kwargs)
        
        # Return an instance of the wrapper
        return MinionToolWrapper()
    
    def batch_to_external(self, tools: List[Any]) -> List[Any]:
        """
        Convert multiple Minion-Manus tools to SmolaAgents tools.
        
        Args:
            tools: The Minion-Manus tools to convert
            
        Returns:
            The converted SmolaAgents tools
        """
        return [self.to_external(tool) for tool in tools]
    
    def batch_from_external(self, external_tools: List[Any]) -> List[Any]:
        """
        Convert multiple SmolaAgents tools to Minion-Manus tools.
        
        Args:
            external_tools: The SmolaAgents tools to convert
            
        Returns:
            The converted Minion-Manus tools
        """
        return [self.from_external(tool) for tool in external_tools]


class AdapterFactory:
    """
    Factory for creating tool adapters.
    
    This class provides methods for creating adapters for various
    ecosystems, making it easy to get the right adapter.
    """
    
    @staticmethod
    def create_adapter(adapter_type: str) -> BaseAdapter:
        """
        Create an adapter of the specified type.
        
        Args:
            adapter_type: The type of adapter to create
            
        Returns:
            The created adapter
            
        Raises:
            ValueError: If the adapter type is not supported
        """
        adapters = {
            "smolagents": SmolaAgentsAdapter,
            # Add more adapter types here
        }
        
        adapter_class = adapters.get(adapter_type.lower())
        if not adapter_class:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
        
        return adapter_class()
    
    @staticmethod
    def get_available_adapters() -> List[str]:
        """
        Get a list of available adapter types.
        
        Returns:
            List of available adapter types
        """
        return ["smolagents"] 