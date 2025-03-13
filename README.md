# Minion-Manus

Minion-Manus is a framework that combines the Minion agent framework with browser use capabilities from OpenManus. It provides a comprehensive solution for building AI agents that can interact with web browsers.

## Features

- **Minion Framework Integration**: Leverages the core capabilities of the Minion framework for agent development.
- **Browser Automation**: Integrates browser-use capabilities from OpenManus for web interaction.
- **Flexible Architecture**: Designed to be modular and extensible for various use cases.

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