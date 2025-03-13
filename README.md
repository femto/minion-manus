# Minion-Manus

Minion-Manus is a framework that combines the Minion agent framework with browser use capabilities from OpenManus. It provides a comprehensive solution for building AI agents that can interact with web browsers.

## Features

- **Minion Framework Integration**: Leverages the core capabilities of the Minion framework for agent development.
- **Browser Automation**: Integrates browser-use capabilities from OpenManus for web interaction.
- **Flexible Architecture**: Designed to be modular and extensible for various use cases.
- **SmolaAgents Compatibility**: Includes an adapter for seamless integration with SmolaAgents library, supporting both synchronous and asynchronous operations.

## Installation

Minion-Manus depends on the Minion framework. Follow these steps to set up both projects:

### 1. Install Minion Framework

```bash
# Clone the Minion repository
git clone https://github.com/femto/minion.git
cd minion

# Install Minion in development mode
pip install -e .

# Note the installation directory path, you'll need it later
MINION_PATH=$(pwd)

# Configure Minion
cp config/config.yaml.example config/config.yaml
cp config/.env.example config/.env

# Edit the configuration files with your API keys and settings
# Edit config/config.yaml for model configurations
# Edit config/.env for API keys

cd ..
```

### 2. Install Minion-Manus

```bash
# Clone the Minion-Manus repository
git clone https://github.com/femto/minion-manus.git
cd minion-manus

# Install Minion-Manus in development mode
pip install -e .
```

### 3. Configure Environment

Set the `MINION_ROOT` environment variable to point to your Minion installation:

```bash
# For bash/zsh (add to your .bashrc or .zshrc)
export MINION_ROOT=/path/to/minion

# For Windows (set as system environment variable)
# MINION_ROOT=C:\path\to\minion
```

Replace `/path/to/minion` with the actual path to your Minion installation (the `MINION_PATH` from step 1).

The Minion-Manus project will use the configuration files from the Minion installation, so make sure your Minion configuration is properly set up with the necessary API keys and model settings.

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
from minion import config
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
- Minion framework (installed as per instructions above)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Minion](https://github.com/femto/minion) - The core agent framework
- [OpenManus](https://github.com/femto/OpenManus) - For browser use capabilities
- [SmolaAgents](https://github.com/huggingface/smolagents) - For agent capabilities 