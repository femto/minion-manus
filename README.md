# Minion-Manus

Minion-Manus is a framework that combines the Minion agent framework with browser use capabilities from OpenManus. It provides a comprehensive solution for building AI agents that can interact with web browsers.

## Features

- **Minion Framework Integration**: Leverages the core capabilities of the Minion framework for agent development.
- **Browser Automation**: Integrates browser-use capabilities from OpenManus for web interaction.
- **Flexible Architecture**: Designed to be modular and extensible for various use cases.
- **SmolaAgents Compatibility**: Includes an adapter for seamless integration with SmolaAgents library, supporting both synchronous and asynchronous operations.

## Installation

```bash
# Clone the repository
git clone https://github.com/femto/minion-manus.git
cd minion-manus

# Install the package
pip install -e .
```

## Quick Start

```python
import asyncio
from minion_manus import Agent
from minion_manus.tools import BrowserTool

async def main():
    # Initialize an agent with browser capabilities
    agent = Agent()
    
    # Add browser tool to the agent
    browser_tool = BrowserTool()
    agent.add_tool(browser_tool)
    
    # Run a task with the agent
    result = await agent.run("Search for 'Python programming' and summarize the first result")
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## SmolaAgents Integration

Minion-Manus provides a seamless integration with the SmolaAgents library through the `MinionProviderAdapter` class. This adapter allows you to use Minion LLM providers with SmolaAgents' `CodeAgent` and `ToolCallingAgent`.

### Synchronous and Asynchronous Support

The adapter supports both synchronous and asynchronous operations:

```python
from minion.providers import create_llm_provider
from minion_manus.examples.smolagents_adapter import MinionProviderAdapter
from smolagents import CodeAgent

# Setup model
llm_config = config.models.get("gpt-4o")
llm_provider = create_llm_provider(llm_config)

# Create the adapter
llm = MinionProviderAdapter(llm_provider)

# Create a CodeAgent with the adapter
agent = CodeAgent(
    tools=[...],
    model=llm,
    max_steps=5
)

# Run the agent synchronously
result = agent.run("Your task here")

# Or run asynchronously
async_result = await agent.arun("Your async task here")
```

The synchronous implementation uses threading and `nest_asyncio` to handle event loop conflicts, making it possible to use the adapter in both synchronous and asynchronous contexts without issues.

## Examples

Check out the `examples` directory for more detailed examples of how to use Minion-Manus.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Minion](https://github.com/yourusername/minion1) - The core agent framework
- [OpenManus](https://github.com/yourusername/OpenManus) - For browser use capabilities
- [SmolaAgents](https://github.com/huggingface/smolagents) - For agent capabilities 