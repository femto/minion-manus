# 异步工具示例
from typing import Dict, Any

import aiohttp

from minion_manus.tools.base_tool import BaseTool


class WeatherTool(BaseTool):
    name = "weather"
    description = "Get current weather for a location"

    async def _execute(self, location: str) -> Dict[str, Any]:
        # 使用aiohttp等进行异步API调用
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.weather.com/{location}") as response:
                return await response.json()


# 同步操作的工具示例（但仍使用异步接口）
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform math calculations"

    async def _execute(self, expression: str) -> float:
        # 简单同步操作，但保持异步接口一致性
        result = eval(expression)
        return result