import asyncio
from typing import List, Dict, Any

from examples.tools.tools_example import WeatherTool, CalculatorTool

from minion_manus import Agent,ToolExecutor

from minion_manus.tools.default_tools import DuckDuckGoSearchTool


# ==== 使用示例 ====
async def main():
    # 1. 创建工具
    tools = [
        CalculatorTool(),
        DuckDuckGoSearchTool(),
        WeatherTool()
    ]

    # 2. 创建工具执行器
    tool_executor = ToolExecutor(tools)

    # 3. 创建Agent
    agent = Agent(tool_executor)

    # 4. 测试不同类型的查询
    queries = [
        "计算2加3乘4等于多少?",
        "北京今天的天气怎么样?",
        "什么是量子计算?",
        "计算10的平方并告诉我北京的天气",
    ]

    for query in queries:
        print("=" * 50)
        response = await agent.execute(query)
        print(response)
        print()


# 运行示例
if __name__ == "__main__":
    asyncio.run(main())