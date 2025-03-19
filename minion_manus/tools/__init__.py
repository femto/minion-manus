"""
工具模块，提供工具基类和装饰器支持。

此模块包含：
1. 基本工具类 - BaseTool
2. 适配器工具类 - SmolTool, MCPTool
3. 装饰器支持 - @tool 装饰器
4. 工具注册表 - registry
"""

from minion_manus.tools.base_tool import BaseTool
from minion_manus.tools.tool_adapter import SmolTool, MCPTool, registry
from minion_manus.tools.decorators import tool

# 导出装饰器
try:
    from minion_manus.tools.decorators import tool
except ImportError:
    # 如果装饰器模块尚未实现或导入失败，提供一个占位符
    def tool(*args, **kwargs):
        """工具装饰器的占位符，实际功能尚未实现"""
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda f: f

__all__ = ["BaseTool", "SmolTool", "MCPTool", "tool", "registry"] 