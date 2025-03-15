import inspect
from typing import List, Dict, Any

from minion_manus.tools.base_tool import BaseTool


class ToolExecutor:
    def __init__(self, tools: List[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool = self.tools[tool_name]
        result = tool.execute(**kwargs)

        if inspect.isawaitable(result):
            return await result
        return result

class Agent:
    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    async def plan(self, user_query: str) -> List[Dict[str, Any]]:
        """根据用户查询规划要执行的工具操作"""
        # 这里是简化版的规划逻辑，实际应用中可能更复杂
        plan = []

        if "calculate" in user_query or "math" in user_query:
            # 提取表达式 (简化示例)
            expression = "2 + 3 * 4"
            plan.append({"tool": "calculator", "params": {"expression": expression}})

        if "weather" in user_query:
            # 提取位置 (简化示例)
            location = "Beijing"
            plan.append({"tool": "weather", "params": {"location": location}})

        if not plan or "search" in user_query:
            plan.append({"tool": "search", "params": {"query": user_query}})

        return plan

    async def execute(self, user_query: str) -> str:
        """执行用户查询并返回结果"""
        # 1. 规划要执行的工具
        actions = await self.plan(user_query)

        # 2. 执行工具调用
        results = []
        for action in actions:
            tool_name = action["tool"]
            params = action.get("params", {})

            try:
                result = await self.tool_executor.execute_tool(tool_name, **params)
                results.append({"tool": tool_name, "result": result})
            except Exception as e:
                results.append({"tool": tool_name, "error": str(e)})

        # 3. 合成回答
        response = self._generate_response(user_query, results)
        return response

    def _generate_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """根据工具执行结果生成回答"""
        # 简化版的回答生成
        response_parts = [f"查询: {query}\n\n结果:"]

        for result in results:
            tool = result["tool"]
            if "error" in result:
                response_parts.append(f"- {tool}: 执行出错 ({result['error']})")
            else:
                response_parts.append(f"- {tool}: {result['result']}")

        return "\n".join(response_parts)