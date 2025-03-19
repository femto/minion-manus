#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用 Minion Manus 工具装饰器的示例。

此示例展示如何使用 @tool 装饰器将函数转换为工具，并在代理中使用它们。
"""

import os
import sys
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union

# 添加父目录到路径以便导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入工具装饰器
try:
    from minion_manus.tools.decorators import tool
    from minion_manus.tools.tool_adapter import registry
    HAS_TOOLS = True
except ImportError as e:
    logger.error(f"导入工具装饰器失败: {e}")
    # 创建一个占位符装饰器
    def tool(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda f: f
    
    # 创建一个模拟的注册表
    class MockRegistry:
        def __init__(self):
            self.tools = {}
        
        def register_tool(self, name, tool):
            self.tools[name] = tool
            
        def get_tool(self, name):
            return self.tools.get(name)
            
        def get_all_tools(self):
            return self.tools
    
    registry = MockRegistry()
    HAS_TOOLS = False


# 基本用法：直接将函数转换为工具
@tool
def search_web(query: str) -> str:
    """在网络上搜索信息
    
    Args:
        query: 搜索查询
        
    Returns:
        搜索结果
    """
    # 这是一个模拟实现
    logger.info(f"搜索网络: {query}")
    return f"关于 '{query}' 的搜索结果：这是一些模拟的搜索数据..."


# 带参数用法：指定工具名称和描述
@tool(name="weather", description="获取天气信息，支持多种温度单位")
def get_weather(location: str, unit: str = "celsius") -> str:
    """获取指定地点的天气信息
    
    Args:
        location: 地点名称，例如：北京、上海、东京
        unit: 温度单位，支持 celsius 或 fahrenheit
        
    Returns:
        天气信息字符串
    """
    # 这是一个模拟实现
    weather_data = {
        "北京": {"celsius": 20, "fahrenheit": 68},
        "上海": {"celsius": 25, "fahrenheit": 77},
        "东京": {"celsius": 22, "fahrenheit": 72},
        "纽约": {"celsius": 15, "fahrenheit": 59},
    }
    
    location = location.lower()
    unit = unit.lower()
    
    if location in weather_data:
        temp = weather_data[location].get(unit, 0)
        return f"{location}的当前天气是：{temp}°{unit}"
    else:
        return f"没有找到{location}的天气信息"


# 复杂返回类型示例
@tool(name="calculator")
def calculate(expression: str) -> Dict[str, Union[str, float]]:
    """计算数学表达式的结果
    
    Args:
        expression: 数学表达式，例如：1 + 2 * 3
        
    Returns:
        包含原始表达式和计算结果的字典
    """
    try:
        # 安全地计算表达式
        # 注意：实际应用中应该更安全地实现这个功能
        result = eval(expression)
        return {
            "expression": expression,
            "result": float(result)
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e)
        }


# 同步版本工具
@tool(name="fetch_data")
def fetch_data_sync(url: str, timeout: int = 10) -> Dict[str, Any]:
    """从URL获取数据
    
    Args:
        url: 要请求的URL
        timeout: 超时时间(秒)
        
    Returns:
        包含状态码和响应内容的字典
    """
    # 这是一个模拟实现
    logger.info(f"请求URL：{url}，超时：{timeout}秒")
    
    # 模拟网络延迟和响应
    import time
    time.sleep(0.5)  # 模拟网络延迟
    
    return {
        "url": url,
        "status": 200,
        "content": f"URL {url} 的模拟响应内容"
    }


# 异步版本工具
@tool(name="fetch_data_async")  # 不指定 tool_type，让工具自动检测
async def fetch_data_async(url: str, timeout: int = 10) -> Dict[str, Any]:
    """从URL异步获取数据
    
    Args:
        url: 要请求的URL
        timeout: 超时时间(秒)
        
    Returns:
        包含状态码和响应内容的字典
    """
    # 这是一个模拟实现
    logger.info(f"异步请求URL：{url}，超时：{timeout}秒")
    
    # 模拟网络延迟
    await asyncio.sleep(0.5)
    
    return {
        "url": url,
        "status": 200,
        "content": f"URL {url} 的异步模拟响应内容"
    }


# 创建一个运行异步函数的辅助函数
def run_async(coro):
    """运行异步函数并返回结果"""
    try:
        # 检查是否已有事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 运行协程并返回结果
        return loop.run_until_complete(coro)
    except Exception as e:
        logger.error(f"运行异步函数失败: {e}")
        raise


async def async_main():
    """异步演示使用工具"""
    print("\n=== 测试异步工具 ===\n")
    
    try:
        # 直接调用异步函数
        result = await fetch_data_async("https://example.com/async")
        print(f"异步获取数据结果: {result}")
        
        # 通过工具实例调用
        async_tool = registry.get_tool("fetch_data_async")
        if async_tool:
            try:
                # 尝试直接调用工具实例上的方法
                result = await async_tool.original_function("https://example.com/via-tool")
                print(f"通过工具原始函数获取数据: {result}")
            except Exception as e:
                print(f"通过工具实例调用失败: {e}")
    except Exception as e:
        print(f"异步工具测试失败: {e}")


def main():
    """演示使用已注册的工具"""
    print("\n=== Minion Manus 工具装饰器示例 ===\n")
    
    if not HAS_TOOLS:
        print("警告: 未能成功导入工具装饰器，使用占位符替代")
    
    # 显示已注册的工具
    tools = registry.get_all_tools()
    print(f"已注册的工具数量: {len(tools)}")
    for name, tool_instance in tools.items():
        print(f"工具名: {name}")
        try:
            print(f"  描述: {tool_instance.description}")
        except Exception as e:
            print(f"  无法获取描述: {e}")
        print()
    
    # 使用工具执行操作
    print("\n=== 使用工具 ===\n")
    
    # 使用 search_web 工具
    try:
        search_result = search_web("Python 编程")
        print(f"搜索结果: {search_result}")
    except Exception as e:
        print(f"搜索工具调用失败: {e}")
    
    # 使用 weather 工具
    try:
        weather_result = get_weather("北京", "celsius")
        print(f"天气信息: {weather_result}")
    except Exception as e:
        print(f"天气工具调用失败: {e}")
    
    # 使用 calculator 工具
    try:
        calc_result = calculate("123 * 456 + 789")
        print(f"计算结果: {calc_result}")
    except Exception as e:
        print(f"计算工具调用失败: {e}")
    
    # 使用 fetch_data 工具
    try:
        fetch_result = fetch_data_sync("https://example.com")
        print(f"获取数据结果: {fetch_result}")
    except Exception as e:
        print(f"获取数据工具调用失败: {e}")
    
    # 获取工具的原始函数
    try:
        print("\n=== 获取工具实例的原始函数 ===\n")
        weather_tool = registry.get_tool("weather")
        if weather_tool:
            original_func = getattr(weather_tool, "original_function", None)
            if original_func:
                print(f"weather 工具的原始函数: {original_func.__name__}")
                print(f"文档字符串: {original_func.__doc__.strip()}")
            else:
                print("weather 工具没有 original_function 属性")
        else:
            print("未找到 weather 工具")
    except Exception as e:
        print(f"获取原始函数失败: {e}")
    
    # 调用异步主函数
    try:
        run_async(async_main())
    except Exception as e:
        print(f"异步主函数执行失败: {e}")
    
    print("\n=== 示例完成 ===\n")


# 以脚本方式运行
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"运行示例时发生错误: {e}")
        print(f"运行示例时发生错误: {e}")
        sys.exit(1) 