# Minion-Manus

A toolkit for implementing and managing tools for LLM agents.

## Overview

Minion-Manus provides a flexible and extensible system for creating, managing, and using tools with Large Language Models (LLMs). It offers a standardized way to define tools, validate their inputs and outputs, and integrate them with various LLM frameworks.

Key features:
- Simple class-based API for defining tools
- Support for both synchronous and asynchronous execution
- Schema validation for inputs and outputs
- Adapters for integration with other tool frameworks
- Comprehensive type hints and documentation

## Installation

```bash
pip install minion-manus
```

## Basic Usage

### Creating a Tool

```python
from minion_manus.tools import Tool

class CalculatorTool(Tool):
    name = "calculator"
    description = "Perform mathematical calculations"
    inputs = {
        "expression": {
            "type": "string",
            "description": "Mathematical expression to evaluate",
            "required": True
        }
    }
    output_type = "number"
    
    def _execute(self, expression: str) -> float:
        return eval(expression)

# Create and use the tool
calculator = CalculatorTool()
result = calculator.execute(expression="2 + 2 * 3")
print(result)  # 8.0
```

### Creating an Async Tool

```python
import asyncio
from minion_manus.tools import AsyncTool

class AsyncCalculatorTool(AsyncTool):
    name = "async_calculator"
    description = "Perform mathematical calculations asynchronously"
    inputs = {
        "expression": {
            "type": "string",
            "description": "Mathematical expression to evaluate",
            "required": True
        }
    }
    output_type = "number"
    
    async def _aexecute(self, expression: str) -> float:
        # Simulate async operation
        await asyncio.sleep(0.1)
        return eval(expression)

# Create and use the async tool
async def main():
    calculator = AsyncCalculatorTool()
    result = await calculator.aexecute(expression="2 + 2 * 3")
    print(result)  # 8.0

    asyncio.run(main())
```

## Tool Schema Definition

Tools are defined with the following schema attributes:

- `name`: A unique identifier for the tool
- `description`: A detailed description of what the tool does
- `inputs`: A dictionary defining the expected input parameters
- `output_type`: The type of the expected output

Input parameters can have the following attributes:
- `type`: Data type (string, number, boolean, object, array)
- `description`: Description of the parameter
- `required`: Whether the parameter is required
- `default`: Default value if not provided

## Adapters

Minion-Manus provides adapters to convert tools between different frameworks. Currently supported:

### SmolaAgents Adapter

Convert between Minion-Manus tools and SmolaAgents tools:

```python
from minion_manus.tools.adapters import AdapterFactory, AdapterType
from smolagents import DuckDuckGoSearchTool

# Convert Minion tool to SmolaAgents tool
calculator = CalculatorTool()
smola_calculator = AdapterFactory.get_adapter(AdapterType.SMOLAGENTS).to_external(calculator)

# Convert SmolaAgents tool to Minion tool
ddg_tool = DuckDuckGoSearchTool()
minion_ddg_tool = AdapterFactory.get_adapter(AdapterType.SMOLAGENTS).to_internal(ddg_tool)
```

## Examples

The repository contains several examples demonstrating different aspects of Minion-Manus:

- `examples/smolagents_adapter_example.py`: Demonstrates how to convert tools between Minion-Manus and SmolaAgents
- `examples/minion_provider_adapter.py`: Shows how to use Minion LLM providers with SmolaAgents
- `examples/database_tool_example.py`: Illustrates creating database tools using SQLAlchemy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.