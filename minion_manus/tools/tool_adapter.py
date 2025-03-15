import inspect
from typing import Any

from minion_manus.tools.base_tool import BaseTool


class ToolAdapter(ABC):
    """工具适配器基类，用于适配不同框架的工具到BaseTool"""

    @abstractmethod
    def adapt(self, external_tool: Any) -> BaseTool:
        """将外部工具适配为BaseTool"""
        pass


class SmolToolAdapter(ToolAdapter):
    """适配smolagents工具的适配器"""

    def adapt(self, smol_tool: Any) -> BaseTool:
        """将smolagents工具适配为BaseTool"""

        class SmolToolWrapper(BaseTool):
            @property
            def name(self) -> str:
                return smol_tool.name

            @property
            def description(self) -> str:
                return smol_tool.description

            def execute(self, **kwargs):
                # 处理同步/异步调用
                result = smol_tool.execute(**kwargs)
                if inspect.isawaitable(result):
                    # 如果是异步结果，返回协程
                    return result
                return result

        return SmolToolWrapper()


class MCPToolAdapter(ToolAdapter):
    """适配MCP工具的适配器"""

    def adapt(self, mcp_tool: Any) -> BaseTool:
        """将MCP工具适配为BaseTool"""

        class MCPToolWrapper(BaseTool):
            @property
            def name(self) -> str:
                return mcp_tool.name

            @property
            def description(self) -> str:
                return mcp_tool.description

            def execute(self, **kwargs):
                # MCP工具特定的调用逻辑
                return mcp_tool.call(**kwargs)

        return MCPToolWrapper()


class ToolRegistry:
    """工具注册中心，管理所有可用的工具适配器"""

    def __init__(self):
        self.adapters = {}

    def register_adapter(self, adapter_name: str, adapter: ToolAdapter):
        """注册一个工具适配器"""
        self.adapters[adapter_name] = adapter

    def adapt(self, adapter_name: str, external_tool: Any) -> BaseTool:
        """使用指定的适配器将外部工具适配为BaseTool"""
        if adapter_name not in self.adapters:
            raise ValueError(f"适配器 '{adapter_name}' 未注册")

        return self.adapters[adapter_name].adapt(external_tool)

registry = ToolRegistry()
registry.register_adapter("smol", SmolToolAdapter())
registry.register_adapter("mcp", MCPToolAdapter())

# 装饰器用法示例
def adapt(adapter_name: str):
    """装饰器，用于将外部工具适配为BaseTool"""
    def decorator(external_tool):
        return registry.adapt(adapter_name, external_tool)
    return decorator
