"""
工具装饰器模块，提供将函数转换为工具的装饰器。
"""

import inspect
import functools
import logging
from typing import Any, Callable, Dict, Optional, Type, Union, get_type_hints

from minion_manus.tools.base import BaseTool
from minion_manus.tools.tool_adapter import SmolTool, MCPTool, registry

# 设置日志
logger = logging.getLogger(__name__)

# 类型映射
TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    None: "null",
    type(None): "null",
    Any: "any",
}


def parse_docstring_params(func):
    """从函数文档字符串提取参数描述
    
    Args:
        func: 要解析文档字符串的函数
        
    Returns:
        包含参数名和描述的字典
    """
    doc = inspect.getdoc(func)
    if not doc:
        return {}
    
    param_docs = {}
    # 简单解析，可以根据需要增强
    if "Args:" in doc:
        try:
            params_section = doc.split("Args:")[1].split("\n\n")[0]
            for line in params_section.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                if ":" in line:
                    param_name, param_desc = line.split(":", 1)
                    param_docs[param_name.strip()] = param_desc.strip()
        except Exception:
            # 解析失败时返回空字典
            pass
    
    return param_docs


def convert_type_to_string(type_hint):
    """将类型提示转换为字符串表示
    
    Args:
        type_hint: 类型提示对象
        
    Returns:
        类型的字符串表示
    """
    if type_hint in TYPE_MAP:
        return TYPE_MAP[type_hint]
    
    # 尝试处理泛型类型
    origin = getattr(type_hint, "__origin__", None)
    if origin is not None:
        if origin is list or origin is set:
            return "array"
        if origin is dict:
            return "object"
        if origin is Union:
            # 对于 Union 类型，选择第一个非 None 类型
            args = getattr(type_hint, "__args__", [])
            for arg in args:
                if arg is not type(None):
                    return convert_type_to_string(arg)
    
    # 默认为字符串类型
    return "string"


def create_base_tool(func, name, description, inputs, output_type="string"):
    """创建基本工具实例
    
    Args:
        func: 要封装的函数
        name: 工具名称
        description: 工具描述
        inputs: 工具输入参数描述
        output_type: 输出类型
        
    Returns:
        工具实例
    """
    class DynamicTool(BaseTool):
        def __init__(self):
            self._func = func
            self._name = name
            self._description = description
            self._inputs = inputs
            self._output_type = output_type
            self.original_function = func
        
        @property
        def name(self) -> str:
            return self._name
        
        @property
        def description(self) -> str:
            return self._description
        
        def _execute(self, *args, **kwargs):
            """执行原始函数并返回结果
            
            支持位置参数和关键字参数
            """
            # 获取原始函数参数签名
            sig = inspect.signature(self._func)
            param_names = list(sig.parameters.keys())
            
            # 如果只有位置参数且第一个位置参数可能是 self，跳过它
            if args and len(param_names) > 0 and param_names[0] == 'self' and len(args) == len(param_names):
                args = args[1:]
            
            try:
                return self._func(*args, **kwargs)
            except Exception as e:
                logger.error(f"执行工具 {self._name} 失败: {e}")
                raise
    
    return DynamicTool()


def create_smol_tool_wrapper(func, name, description, inputs, output_type="string"):
    """创建适合 SmolaAgents 使用的工具包装
    
    这个函数假设 SmolaAgents 已安装，并创建一个符合其 Tool 规范的对象
    
    Args:
        func: 要封装的函数
        name: 工具名称
        description: 工具描述
        inputs: 工具输入参数描述
        output_type: 输出类型
        
    Returns:
        符合 SmolaAgents 规范的工具对象
    """
    try:
        from smolagents.tools import Tool as SmolaAgentsTool
        
        # 转换输入格式为 SmolaAgents 格式
        smol_inputs = {}
        for param_name, param_info in inputs.items():
            smol_inputs[param_name] = {
                "type": param_info["type"],
                "description": param_info["description"]
            }
            if "nullable" in param_info:
                smol_inputs[param_name]["nullable"] = param_info["nullable"]
                
            if "default" in param_info:
                # 不要在 inputs 中放入默认值，这会导致 SmolaAgents 验证失败
                # smol_inputs[param_name]["default"] = param_info["default"]
                pass
        
        # 创建一个 SmolaAgentsTool 子类
        tool_name = name  # 创建局部变量避免类定义中直接使用外部变量
        tool_description = description
        tool_inputs = smol_inputs
        tool_output_type = output_type
        
        # 获取原始函数的参数列表
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        is_async = inspect.iscoroutinefunction(func)
        
        # 创建一个动态的 forward 方法，参数与 inputs 匹配
        if is_async:
            # 异步方法需要特殊处理
            async def dynamic_forward(self, **kwargs):
                # 只传入存在于原始函数中的参数
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in param_names}
                return await func(**filtered_kwargs)
        else:
            # 同步方法
            def dynamic_forward(self, **kwargs):
                # 只传入存在于原始函数中的参数
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in param_names}
                return func(**filtered_kwargs)
        
        # 创建工具类
        class SmolaAgentsToolWrapper(SmolaAgentsTool):
            name = tool_name
            description = tool_description
            inputs = tool_inputs
            output_type = tool_output_type
            
            # 使用动态生成的 forward 方法
            forward = dynamic_forward
        
        # 保存原始函数引用
        SmolaAgentsToolWrapper.original_function = func
        
        # 返回实例
        return SmolaAgentsToolWrapper()
    except ImportError:
        logger.warning(f"未找到 SmolaAgents 包，创建模拟对象")
        # 如果没有安装 SmolaAgents，创建一个模拟对象
        class MockSmolaAgentsTool:
            def __init__(self):
                self.name = name
                self.description = description
                self.inputs = inputs
                self.output_type = output_type
                self.original_function = func
                
            def execute(self, **kwargs):
                return func(**kwargs)
        
        return MockSmolaAgentsTool()


def tool(func=None, *, name=None, description=None, tool_type=None, register=True):
    """将函数转换为 Minion Manus Tool 的装饰器
    
    可以直接使用：@tool
    或者带参数使用：@tool(name="my_tool", description="描述")
    
    Args:
        func: 要转换的函数
        name: 工具名称，默认为函数名
        description: 工具描述，默认从函数文档字符串提取
        tool_type: 工具类型，决定使用哪个适配器类
        register: 是否自动注册到工具注册表
        
    Returns:
        工具实例
    """
    def decorator(func):
        # 提取工具元数据
        tool_name = name or func.__name__
        tool_description = description or inspect.getdoc(func) or "未提供描述"
        
        # 提取函数返回类型
        type_hints = get_type_hints(func)
        return_type = type_hints.get('return', Any)
        output_type = convert_type_to_string(return_type)
        
        # 提取参数信息
        sig = inspect.signature(func)
        param_docs = parse_docstring_params(func)
        
        inputs = {}
        for param_name, param in sig.parameters.items():
            # 跳过 self 参数
            if param_name == 'self':
                continue
                
            param_type_hint = type_hints.get(param_name, str)
            param_type = convert_type_to_string(param_type_hint)
            
            param_desc = param_docs.get(param_name, "")
            inputs[param_name] = {
                "type": param_type,
                "description": param_desc
            }
            
            # 处理默认值
            if param.default != inspect.Parameter.empty:
                inputs[param_name]["default"] = param.default
                inputs[param_name]["nullable"] = True
        
        # 检查是否是异步函数
        is_async = inspect.iscoroutinefunction(func)
        
        # 确定工具类型和适配器
        if tool_type == "smol" and not is_async:
            # 对于非异步函数，使用 SmolaAgents 兼容工具
            logger.debug(f"为函数 {func.__name__} 创建 SmolTool 适配器")
            # 创建 SmolaAgents 兼容工具
            smol_tool = create_smol_tool_wrapper(func, tool_name, tool_description, inputs, output_type)
            # 使用适配器包装
            tool_instance = SmolTool(smol_tool)
        elif tool_type == "mcp":
            # 创建 MCP 兼容工具
            logger.warning(f"MCP 工具类型尚未完全实现，功能可能受限")
            base_tool = create_base_tool(func, tool_name, tool_description, inputs, output_type)
            tool_instance = MCPTool(base_tool)
        else:
            # 默认使用普通的 BaseTool 实现
            # 如果是异步函数但用户显式指定了smol类型，需要发出警告
            if is_async and tool_type == "smol":
                logger.warning(f"异步函数 {func.__name__} 不适用于smol适配器，将使用基本工具类型")
            
            tool_instance = create_base_tool(func, tool_name, tool_description, inputs, output_type)
        
        # 保留原始函数的引用
        tool_instance.original_function = func
        
        # 自动注册到全局注册表
        if register:
            logger.debug(f"注册工具: {tool_name}")
            registry.register_tool(tool_name, tool_instance)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if is_async:
                logger.warning(f"异步函数 {func.__name__} 应该使用 await 调用，而不是直接调用")
                # 对于异步函数，返回协程对象
                return func(*args, **kwargs)
            # 对于同步函数，直接调用工具实例的 _execute 方法
            try:
                return tool_instance._execute(*args, **kwargs)
            except Exception as e:
                logger.error(f"执行工具 {tool_name} 失败: {e}")
                # 尝试直接调用原始函数作为后备方案
                return func(*args, **kwargs)
        
        # 将工具实例附加到包装函数
        wrapper.tool = tool_instance
        return wrapper
    
    if func is None:
        # 用作装饰器工厂
        return decorator
    
    # 作为直接装饰器使用
    return decorator(func) 