# Minion Manus

A simplified wrapper for smolagents that makes it easy to create and run AI agents.

## Installation

```bash
pip install minion-manus
```

## Usage

Here's a simple example of how to use Minion Manus:

```python
from minion_manus import MinionAgent, AgentConfig

# Configure the agent
agent_config = AgentConfig(
    model_id="gpt-4",  # or your preferred model
    name="Research Assistant",
    description="A helpful research assistant",
    instructions="You are a helpful research assistant that can search the web and visit webpages.",
    tools=["web_search", "visit_webpage"],
    model_args={"api_key_var": "OPENAI_API_KEY"}  # Will use OPENAI_API_KEY from environment
)

# Create and run the agent
agent = MinionAgent(agent_config)

# Run the agent with a question
result = agent.run("What are the latest developments in AI?")
print("Agent's response:", result)
```

## Configuration

The `AgentConfig` class accepts the following parameters:

- `model_id`: The ID of the model to use (e.g., "gpt-4")
- `name`: Name of the agent (default: "Minion")
- `description`: Optional description of the agent
- `instructions`: Optional system instructions for the agent
- `tools`: List of tools the agent can use
- `model_args`: Optional dictionary of model-specific arguments
- `agent_args`: Optional dictionary of agent-specific arguments

## Environment Variables

Make sure to set up your environment variables in a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/yourusername/minion-manus.git
cd minion-manus

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## License

MIT License