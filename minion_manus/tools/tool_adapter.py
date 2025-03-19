import inspect
from abc import ABC, abstractmethod
from typing import Any

from minion_manus.tools.base_tool import BaseTool


class SmolTool(BaseTool):
    """适配smolagents工具的适配器"""
    
    def __init__(self, smol_tool: Any):
        """初始化SmolTool
        
        Args:
            smol_tool: SmolaAgents工具实例
        """
        self._smol_tool = smol_tool
    
    @property
    def name(self) -> str:
        """获取工具名称"""
        return self._smol_tool.name
    
    @property
    def description(self) -> str:
        """获取工具描述"""
        return self._smol_tool.description
    
    @property
    def original_tool(self) -> Any:
        """获取原始的SmolaAgents工具实例
        
        Returns:
            原始的SmolaAgents工具实例
        """
        return self._smol_tool
    
    def get_smolagents_tool(self) -> Any:
        """获取原始的SmolaAgents工具实例，用于传递给SmolaAgents框架
        
        Returns:
            原始的SmolaAgents工具实例
        """
        return self._smol_tool
    
    def _execute(self, **kwargs) -> Any:
        """执行工具函数
        
        Args:
            **kwargs: 传递给SmolaAgents工具的参数
            
        Returns:
            工具执行结果
        """
        # 处理同步/异步调用
        result = self._smol_tool.execute(**kwargs)
        if inspect.isawaitable(result):
            # 如果是异步结果，返回协程
            return result
        return result


class MCPTool(BaseTool):
    """适配MCP工具的适配器"""
    
    def __init__(self, mcp_tool: Any):
        """初始化MCPTool
        
        Args:
            mcp_tool: MCP工具实例
        """
        self._mcp_tool = mcp_tool
    
    @property
    def name(self) -> str:
        """获取工具名称"""
        return self._mcp_tool.name
    
    @property
    def description(self) -> str:
        """获取工具描述"""
        return self._mcp_tool.description
    
    @property
    def original_tool(self) -> Any:
        """获取原始的MCP工具实例
        
        Returns:
            原始的MCP工具实例
        """
        return self._mcp_tool
    
    def get_mcp_tool(self) -> Any:
        """获取原始的MCP工具实例，用于传递给MCP框架
        
        Returns:
            原始的MCP工具实例
        """
        return self._mcp_tool
    
    def _execute(self, **kwargs) -> Any:
        """执行工具函数
        
        Args:
            **kwargs: 传递给MCP工具的参数
            
        Returns:
            工具执行结果
        """
        # MCP工具特定的调用逻辑
        return self._mcp_tool.call(**kwargs)


class ToolRegistry:
    """工具注册中心，管理所有可用的工具适配器"""
    
    def __init__(self):
        """初始化工具注册中心"""
        self.tools = {}
    
    def register_tool(self, tool_name: str, tool: BaseTool):
        """注册一个工具
        
        Args:
            tool_name: 工具名称
            tool: 工具实例
        """
        self.tools[tool_name] = tool
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """获取指定的工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例
            
        Raises:
            ValueError: 如果工具未注册
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 未注册")
        
        return self.tools[tool_name]
    
    def get_all_tools(self) -> dict:
        """获取所有已注册的工具
        
        Returns:
            工具字典，键为工具名称，值为工具实例
        """
        return self.tools.copy()
    
    def get_original_tools(self) -> dict:
        """获取所有已注册工具的原始实例
        
        Returns:
            工具字典，键为工具名称，值为原始工具实例
        """
        original_tools = {}
        for name, tool in self.tools.items():
            if hasattr(tool, 'original_tool'):
                original_tools[name] = tool.original_tool
            else:
                original_tools[name] = tool
        return original_tools


# 创建全局注册中心实例
registry = ToolRegistry()


# 工具创建函数
def create_smol_tool(smol_tool: Any) -> SmolTool:
    """创建SmolaAgents工具适配器
    
    Args:
        smol_tool: SmolaAgents工具实例
        
    Returns:
        适配后的工具实例
    """
    return SmolTool(smol_tool)


def create_mcp_tool(mcp_tool: Any) -> MCPTool:
    """创建MCP工具适配器
    
    Args:
        mcp_tool: MCP工具实例
        
    Returns:
        适配后的工具实例
    """
    return MCPTool(mcp_tool)


# 获取原始工具的辅助函数
def get_original_tool(tool: BaseTool) -> Any:
    """获取工具的原始实例
    
    Args:
        tool: 适配后的工具实例
        
    Returns:
        原始工具实例，如果没有则返回工具本身
    """
    if hasattr(tool, 'original_tool'):
        return tool.original_tool
    return tool


# 装饰器用法
def register_tool(tool_name: str):
    """将工具注册到全局注册中心的装饰器
    
    Args:
        tool_name: 工具名称
        
    Returns:
        装饰器函数
    """
    def decorator(tool_class):
        tool = tool_class()
        registry.register_tool(tool_name, tool)
        return tool_class
    return decorator

