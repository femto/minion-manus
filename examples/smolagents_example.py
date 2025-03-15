#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Example script demonstrating the use of CodeAgent and ToolCallingAgent from smolagents.
This example shows how to create custom tools, initialize agents, and run them with different tasks.

@Time    : 2024/7/15 10:00
@Author  : femto Zheng
@File    : smolagents_example.py
"""
import asyncio
import os
import time
from typing import List, Dict, Any, Optional

import yaml
from rich.console import Console
from rich.panel import Panel

from minion import config
from minion.main import LocalPythonEnv
from minion.main.brain import Brain
from minion.providers import create_llm_provider

# Import smolagents classes
from smolagents import CodeAgent, ToolCallingAgent
from smolagents.monitoring import LogLevel
from smolagents.memory import AgentMemory
from smolagents.tools import Tool
from smolagents.default_tools import PythonInterpreterTool, DuckDuckGoSearchTool, VisitWebpageTool, FinalAnswerTool

# Import our adapter
from minion_manus.examples.smolagents_adapter import MinionProviderAdapter


# Create a custom calculator tool
class CalculatorTool(Tool):
    name = "calculator"
    description = "A simple calculator that can perform basic arithmetic operations."
    inputs = {
        "expression": {
            "type": "string",
            "description": "The arithmetic expression to evaluate (e.g., '2 + 2', '3 * 4', etc.)"
        }
    }
    output_type = "string"

    def forward(self, expression: str) -> str:
        try:
            # Safely evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"


# Create a custom database query tool
class DatabaseQueryTool(Tool):
    name = "database_query"
    description = "Simulates querying a database for information."
    inputs = {
        "query": {
            "type": "string",
            "description": "The SQL-like query to execute"
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__()
        # Simulate a simple database with some data
        self.database = {
            "users": [
                {"id": 1, "name": "Alice", "age": 30, "city": "New York"},
                {"id": 2, "name": "Bob", "age": 25, "city": "San Francisco"},
                {"id": 3, "name": "Charlie", "age": 35, "city": "Chicago"},
                {"id": 4, "name": "Diana", "age": 28, "city": "Boston"},
            ],
            "products": [
                {"id": 101, "name": "Laptop", "price": 1200, "category": "Electronics"},
                {"id": 102, "name": "Smartphone", "price": 800, "category": "Electronics"},
                {"id": 103, "name": "Desk Chair", "price": 250, "category": "Furniture"},
                {"id": 104, "name": "Coffee Maker", "price": 100, "category": "Appliances"},
            ]
        }

    def forward(self, query: str) -> str:
        # This is a very simplified simulation of SQL queries
        query = query.lower()
        
        if "select" not in query:
            return "Error: Query must include SELECT statement"
        
        if "from users" in query:
            table = "users"
        elif "from products" in query:
            table = "products"
        else:
            return "Error: Query must specify a valid table (users or products)"
        
        # Very basic filtering
        results = self.database[table]
        if "where" in query:
            where_clause = query.split("where")[1].strip()
            filtered_results = []
            
            for item in results:
                # Very simplistic condition evaluation
                try:
                    condition_met = eval(where_clause, {"__builtins__": {}}, item)
                    if condition_met:
                        filtered_results.append(item)
                except:
                    pass
            
            results = filtered_results
        
        return f"Query results: {results}"


# Function to run CodeAgent examples
async def run_code_agent_examples():
    console = Console()
    console.print(Panel("[bold blue]Running CodeAgent Examples[/bold blue]"))
    
    # Setup model
    model_name = "gpt-4o"
    llm_config = config.models.get(model_name)
    llm_provider = create_llm_provider(llm_config)
    
    # Create the adapter
    llm = MinionProviderAdapter(llm_provider)
    
    # Define tools for the CodeAgent
    tools = [
        CalculatorTool(),
        DatabaseQueryTool(),
        PythonInterpreterTool(authorized_imports=["math", "numpy", "pandas", "datetime"]),
    ]
    
    # Create the CodeAgent
    code_agent = CodeAgent(
        tools=tools,
        model=llm,
        max_steps=5,
        verbosity_level=LogLevel.INFO,
        additional_authorized_imports=["math", "numpy", "pandas", "datetime"],
    )
    
    # Example 1: Simple calculation task
    console.print("\n[bold cyan]Example 1: Simple Calculation Task[/bold cyan]")
    result = code_agent.run(
        "Calculate the factorial of 5 and then find the square root of the result. "
        "Show your work step by step."
    )
    console.print(f"[green]Result:[/green] {result}")
    
    # Reset the agent for the next example
    code_agent.memory.reset()
    
    # Example 2: Data analysis task
    console.print("\n[bold cyan]Example 2: Data Analysis Task[/bold cyan]")
    result = code_agent.run(
        "Create a list of 10 random numbers between 1 and 100. "
        "Then calculate the mean, median, and standard deviation. "
        "Finally, create a function that identifies outliers (values more than 2 standard deviations from the mean)."
    )
    console.print(f"[green]Result:[/green] {result}")
    
    # Reset the agent for the next example
    code_agent.memory.reset()
    
    # Example 3: Using the database query tool
    console.print("\n[bold cyan]Example 3: Database Query Task[/bold cyan]")
    result = code_agent.run(
        "Query the database to find all users who are older than 25. "
        "Then, query the database to find all products in the Electronics category. "
        "Finally, create a summary of the results."
    )
    console.print(f"[green]Result:[/green] {result}")
    
    return code_agent


# Function to run ToolCallingAgent examples
async def run_tool_calling_agent_examples():
    console = Console()
    console.print(Panel("[bold blue]Running ToolCallingAgent Examples[/bold blue]"))
    
    # Setup model
    model_name = "gpt-4o"
    llm_config = config.models.get(model_name)
    llm_provider = create_llm_provider(llm_config)
    
    # Create the adapter
    llm = MinionProviderAdapter(llm_provider)
    
    # Define tools for the ToolCallingAgent
    tools = [
        CalculatorTool(),
        DatabaseQueryTool(),
        DuckDuckGoSearchTool(max_results=3),
        VisitWebpageTool(),
    ]
    
    # Create the ToolCallingAgent
    tool_agent = ToolCallingAgent(
        tools=tools,
        model=llm,
        max_steps=5,
        verbosity_level=LogLevel.INFO,
    )
    
    # Example 1: Information retrieval and calculation
    console.print("\n[bold cyan]Example 1: Information Retrieval and Calculation[/bold cyan]")
    result = tool_agent.run(
        "What is the capital of Japan and what's the population? "
        "Also, calculate what would be 0.1% of that population."
    )
    console.print(f"[green]Result:[/green] {result}")
    
    # Reset the agent for the next example
    tool_agent.memory.reset()
    
    # Example 2: Database query
    console.print("\n[bold cyan]Example 2: Database Query[/bold cyan]")
    result = tool_agent.run(
        "Query the database to find all products with a price greater than 200. "
        "Then calculate the average price of these products."
    )
    console.print(f"[green]Result:[/green] {result}")
    
    # Reset the agent for the next example
    tool_agent.memory.reset()
    
    # Example 3: Web search and information synthesis
    console.print("\n[bold cyan]Example 3: Web Search and Information Synthesis[/bold cyan]")
    result = tool_agent.run(
        "Find information about the latest developments in quantum computing. "
        "Summarize the key advancements and potential applications."
    )
    console.print(f"[green]Result:[/green] {result}")
    
    return tool_agent


# Function to compare CodeAgent and ToolCallingAgent
async def compare_agents():
    console = Console()
    console.print(Panel("[bold blue]Comparing CodeAgent and ToolCallingAgent[/bold blue]"))
    
    # Setup model
    model_name = "gpt-4o"
    llm_config = config.models.get(model_name)
    llm_provider = create_llm_provider(llm_config)
    
    # Create the adapter
    llm = MinionProviderAdapter(llm_provider)
    
    # Define common tools for both agents
    common_tools = [
        CalculatorTool(),
        DatabaseQueryTool(),
    ]
    
    # Create both agents
    code_agent = CodeAgent(
        tools=common_tools,
        model=llm,
        max_steps=5,
        verbosity_level=LogLevel.INFO,
        additional_authorized_imports=["math"],
    )
    
    tool_agent = ToolCallingAgent(
        tools=common_tools,
        model=llm,
        max_steps=5,
        verbosity_level=LogLevel.INFO,
    )
    
    # Define a common task for both agents
    task = (
        "Find all users in the database who live in New York or Chicago. "
        "Then calculate the average age of these users."
    )
    
    console.print(f"\n[bold cyan]Task for both agents:[/bold cyan] {task}")
    
    # Run CodeAgent
    console.print("\n[bold magenta]Running with CodeAgent:[/bold magenta]")
    start_time = time.time()
    code_result = code_agent.run(task)
    code_time = time.time() - start_time
    console.print(f"[green]Result:[/green] {code_result}")
    console.print(f"[yellow]Time taken:[/yellow] {code_time:.2f} seconds")
    
    # Run ToolCallingAgent
    console.print("\n[bold magenta]Running with ToolCallingAgent:[/bold magenta]")
    start_time = time.time()
    tool_result = tool_agent.run(task)
    tool_time = time.time() - start_time
    console.print(f"[green]Result:[/green] {tool_result}")
    console.print(f"[yellow]Time taken:[/yellow] {tool_time:.2f} seconds")
    
    # Compare results
    console.print("\n[bold cyan]Comparison:[/bold cyan]")
    console.print(f"CodeAgent took {code_time:.2f} seconds")
    console.print(f"ToolCallingAgent took {tool_time:.2f} seconds")
    console.print(f"Difference: {abs(code_time - tool_time):.2f} seconds")
    
    if code_time < tool_time:
        console.print("[bold green]CodeAgent was faster![/bold green]")
    else:
        console.print("[bold green]ToolCallingAgent was faster![/bold green]")


# Function to demonstrate integration with Brain
async def run_brain_integration():
    console = Console()
    console.print(Panel("[bold blue]Demonstrating Integration with Brain[/bold blue]"))
    
    # Setup model
    model_name = "gpt-4o"
    llm_config = config.models.get(model_name)
    llm = create_llm_provider(llm_config)
    
    # Setup Python environment
    python_env = LocalPythonEnv(verbose=False)
    
    # Create Brain instance
    brain = Brain(
        python_env=python_env,
        llm=llm
    )
    
    # Example 1: Using Brain for a coding task (similar to CodeAgent)
    console.print("\n[bold cyan]Example 1: Brain for Coding Task[/bold cyan]")
    obs, score, *_ = await brain.step(
        query="Write a Python function to find the n-th Fibonacci number using dynamic programming.",
        route="python",
        post_processing="extract_python"
    )
    console.print(f"[green]Result:[/green]\n{obs}")
    
    # Example 2: Using Brain for a reasoning task (similar to ToolCallingAgent)
    console.print("\n[bold cyan]Example 2: Brain for Reasoning Task[/bold cyan]")
    obs, score, *_ = await brain.step(
        query="Explain the difference between supervised and unsupervised learning in machine learning.",
        check=False
    )
    console.print(f"[green]Result:[/green]\n{obs}")
    
    # Example 3: Using Brain for a mathematical problem
    console.print("\n[bold cyan]Example 3: Brain for Mathematical Problem[/bold cyan]")
    obs, score, *_ = await brain.step(
        query="Solve the equation: 3x^2 - 12x + 9 = 0",
        route="cot"
    )
    console.print(f"[green]Result:[/green]\n{obs}")


# Define a mapping of base tools similar to TOOL_MAPPING in smolagents
TOOL_MAPPING = {
    "calculator": CalculatorTool,
    "database_query": DatabaseQueryTool,
    "python_interpreter": PythonInterpreterTool,
    "search": DuckDuckGoSearchTool,
    "visit_webpage": VisitWebpageTool,
}

# Function to demonstrate custom tool initialization logic
async def run_custom_tool_initialization_example():
    console = Console()
    console.print(Panel("[bold blue]Demonstrating Custom Tool Initialization Logic[/bold blue]"))
    
    # Explanation of the tool initialization logic
    console.print("""
[bold yellow]Explanation of the Tool Initialization Logic in smolagents:[/bold yellow]

The smolagents library uses the following logic to initialize tools for agents:

1. First, it creates a dictionary of tools from the user-provided tools:
   [cyan]self.tools = {tool.name: tool for tool in tools}[/cyan]

2. If add_base_tools=True (which is the default), it adds base tools from TOOL_MAPPING:
   [cyan]if add_base_tools:
       for tool_name, tool_class in TOOL_MAPPING.items():
           if tool_name != "python_interpreter" or self.__class__.__name__ == "ToolCallingAgent":
               self.tools[tool_name] = tool_class()[/cyan]

3. The conditional [cyan]if tool_name != "python_interpreter" or self.__class__.__name__ == "ToolCallingAgent"[/cyan] means:
   - The python_interpreter tool is only added if the agent is a ToolCallingAgent
   - All other base tools are added regardless of agent type

4. Finally, it always adds a final_answer tool:
   [cyan]self.tools["final_answer"] = FinalAnswerTool()[/cyan]

This ensures that every agent has a way to provide a final answer, and optionally includes 
a set of base tools, with special handling for the Python interpreter tool.
""")
    
    # Setup model
    model_name = "gpt-4o"
    llm_config = config.models.get(model_name)
    llm_provider = create_llm_provider(llm_config)
    
    # Create the adapter
    llm = MinionProviderAdapter(llm_provider)
    
    # Define custom tools
    custom_tools = [
        CalculatorTool(),
    ]
    
    # Example 1: Initialize tools with add_base_tools=True for CodeAgent
    console.print("\n[bold cyan]Example 1: CodeAgent with add_base_tools=True[/bold cyan]")
    
    # Initialize tools dictionary from custom tools
    code_agent_tools = {tool.name: tool for tool in custom_tools}
    
    # Add base tools with the same logic as smolagents
    for tool_name, tool_class in TOOL_MAPPING.items():
        # Only add python_interpreter if this is a ToolCallingAgent
        if tool_name != "python_interpreter" or "CodeAgent" == "ToolCallingAgent":
            code_agent_tools[tool_name] = tool_class()
    
    # Always add final_answer tool
    code_agent_tools["final_answer"] = FinalAnswerTool()
    
    # Print the tools that would be available
    console.print("[yellow]Tools available to CodeAgent:[/yellow]")
    for tool_name in code_agent_tools.keys():
        console.print(f"  - {tool_name}")
    
    # Example 2: Initialize tools with add_base_tools=True for ToolCallingAgent
    console.print("\n[bold cyan]Example 2: ToolCallingAgent with add_base_tools=True[/bold cyan]")
    
    # Initialize tools dictionary from custom tools
    tool_agent_tools = {tool.name: tool for tool in custom_tools}
    
    # Add base tools with the same logic as smolagents
    for tool_name, tool_class in TOOL_MAPPING.items():
        # Only add python_interpreter if this is a ToolCallingAgent
        if tool_name != "python_interpreter" or "ToolCallingAgent" == "ToolCallingAgent":
            tool_agent_tools[tool_name] = tool_class()
    
    # Always add final_answer tool
    tool_agent_tools["final_answer"] = FinalAnswerTool()
    
    # Print the tools that would be available
    console.print("[yellow]Tools available to ToolCallingAgent:[/yellow]")
    for tool_name in tool_agent_tools.keys():
        console.print(f"  - {tool_name}")
    
    # Example 3: Create a custom agent class with the tool initialization logic
    console.print("\n[bold cyan]Example 3: Custom Agent Class with Tool Initialization Logic[/bold cyan]")
    
    class CustomAgent:
        def __init__(self, tools=None, add_base_tools=True):
            # Initialize tools dictionary
            self.tools = {tool.name: tool for tool in (tools or [])}
            
            # Add base tools if requested
            if add_base_tools:
                for tool_name, tool_class in TOOL_MAPPING.items():
                    # Only add python_interpreter if this is a ToolCallingAgent
                    if tool_name != "python_interpreter" or self.__class__.__name__ == "ToolCallingAgent":
                        self.tools[tool_name] = tool_class()
            
            # Always add final_answer tool
            self.tools["final_answer"] = FinalAnswerTool()
    
    # Create instances of CustomAgent with different class names
    class ToolCallingAgent(CustomAgent):
        pass
    
    class CodeAgent(CustomAgent):
        pass
    
    # Create instances
    custom_tool_agent = ToolCallingAgent(tools=custom_tools)
    custom_code_agent = CodeAgent(tools=custom_tools)
    
    # Print the tools available to each agent
    console.print("[yellow]Tools available to custom ToolCallingAgent:[/yellow]")
    for tool_name in custom_tool_agent.tools.keys():
        console.print(f"  - {tool_name}")
    
    console.print("\n[yellow]Tools available to custom CodeAgent:[/yellow]")
    for tool_name in custom_code_agent.tools.keys():
        console.print(f"  - {tool_name}")
    
    # Example 4: Create agents with add_base_tools=False
    console.print("\n[bold cyan]Example 4: Agents with add_base_tools=False[/bold cyan]")
    
    no_base_tool_agent = ToolCallingAgent(tools=custom_tools, add_base_tools=False)
    no_base_code_agent = CodeAgent(tools=custom_tools, add_base_tools=False)
    
    console.print("[yellow]Tools available to ToolCallingAgent with add_base_tools=False:[/yellow]")
    for tool_name in no_base_tool_agent.tools.keys():
        console.print(f"  - {tool_name}")
    
    console.print("\n[yellow]Tools available to CodeAgent with add_base_tools=False:[/yellow]")
    for tool_name in no_base_code_agent.tools.keys():
        console.print(f"  - {tool_name}")


# Function to demonstrate creating a custom agent with smolagents tool initialization logic
async def create_custom_agent_with_smolagents_logic():
    console = Console()
    console.print(Panel("[bold blue]Creating Custom Agent with SmolaAgents Tool Logic[/bold blue]"))
    
    # Setup model
    model_name = "gpt-4o"
    llm_config = config.models.get(model_name)
    llm_provider = create_llm_provider(llm_config)
    
    # Create the adapter
    llm = MinionProviderAdapter(llm_provider)
    
    # Create a base Agent class with smolagents-like tool initialization
    class BaseAgent:
        def __init__(self, tools=None, add_base_tools=True, model=None, max_steps=5, verbosity_level=LogLevel.INFO):
            # Store the model and other parameters
            self.model = model
            self.max_steps = max_steps
            self.verbosity_level = verbosity_level
            self.memory = AgentMemory()
            
            # Initialize tools dictionary from user-provided tools
            self.tools = {tool.name: tool for tool in (tools or [])}
            
            # Add base tools if requested (same logic as smolagents)
            if add_base_tools:
                for tool_name, tool_class in TOOL_MAPPING.items():
                    # Only add python_interpreter if this is a ToolCallingAgent
                    if tool_name != "python_interpreter" or self.__class__.__name__ == "ToolCallingAgent":
                        self.tools[tool_name] = tool_class()
            
            # Always add final_answer tool
            self.tools["final_answer"] = FinalAnswerTool()
        
        def run(self, query):
            # Simple implementation to demonstrate tool access
            available_tools = list(self.tools.keys())
            return f"Agent would process query: '{query}' using available tools: {available_tools}"
    
    # Create specialized agent classes
    class CustomCodeAgent(BaseAgent):
        def __init__(self, tools=None, add_base_tools=True, model=None, max_steps=5, verbosity_level=LogLevel.INFO, 
                     additional_authorized_imports=None):
            super().__init__(tools, add_base_tools, model, max_steps, verbosity_level)
            self.additional_authorized_imports = additional_authorized_imports or []
    
    class CustomToolCallingAgent(BaseAgent):
        pass  # Inherits everything from BaseAgent
    
    # Create instances with different configurations
    console.print("\n[bold cyan]Creating agents with different configurations:[/bold cyan]")
    
    # Define some custom tools
    custom_tools = [CalculatorTool(), DatabaseQueryTool()]
    
    # Create a CodeAgent with default settings (add_base_tools=True)
    code_agent = CustomCodeAgent(
        tools=custom_tools,
        model=llm,
        additional_authorized_imports=["math", "numpy"]
    )
    
    # Create a ToolCallingAgent with default settings (add_base_tools=True)
    tool_agent = CustomToolCallingAgent(
        tools=custom_tools,
        model=llm
    )
    
    # Create a CodeAgent with add_base_tools=False
    code_agent_no_base = CustomCodeAgent(
        tools=custom_tools,
        model=llm,
        add_base_tools=False
    )
    
    # Print the available tools for each agent
    console.print("\n[yellow]Tools available to CustomCodeAgent (with add_base_tools=True):[/yellow]")
    for tool_name in code_agent.tools.keys():
        console.print(f"  - {tool_name}")
    
    console.print("\n[yellow]Tools available to CustomToolCallingAgent (with add_base_tools=True):[/yellow]")
    for tool_name in tool_agent.tools.keys():
        console.print(f"  - {tool_name}")
    
    console.print("\n[yellow]Tools available to CustomCodeAgent (with add_base_tools=False):[/yellow]")
    for tool_name in code_agent_no_base.tools.keys():
        console.print(f"  - {tool_name}")
    
    # Demonstrate running the agents
    console.print("\n[bold cyan]Running the custom agents:[/bold cyan]")
    
    query = "Calculate 2+2 and then query the database for users in New York"
    
    code_result = code_agent.run(query)
    tool_result = tool_agent.run(query)
    
    console.print(f"\n[green]CustomCodeAgent result:[/green] {code_result}")
    console.print(f"[green]CustomToolCallingAgent result:[/green] {tool_result}")
    
    return code_agent, tool_agent


# Main function to run all examples
async def main():
    console = Console()
    console.print(Panel("[bold yellow]SmolaAgents Examples[/bold yellow]", subtitle="Demonstrating CodeAgent and ToolCallingAgent"))
    
    # Run CodeAgent examples
    code_agent = await run_code_agent_examples()
    
    # Run ToolCallingAgent examples
    tool_agent = await run_tool_calling_agent_examples()
    
    # Compare the agents
    await compare_agents()
    
    # Demonstrate integration with Brain
    await run_brain_integration()
    
    # Run the custom tool initialization example
    await run_custom_tool_initialization_example()
    
    # Create custom agents with smolagents tool logic
    await create_custom_agent_with_smolagents_logic()
    
    console.print(Panel("[bold green]All examples completed successfully![/bold green]"))


if __name__ == "__main__":
    asyncio.run(main()) 