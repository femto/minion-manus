# SmolaAgents Adapter for Minion-Manus

This directory contains an adapter that allows Minion LLM providers to be used with the SmolaAgents library. The adapter provides a bridge between the two frameworks, enabling you to leverage the capabilities of both.

## Prerequisites

Before using this adapter, ensure you have:

1. Installed the Minion framework:
   ```bash
   git clone https://github.com/femto/minion.git
   cd minion
   pip install -e .
   
   # Configure Minion
   cp config/config.yaml.example config/config.yaml
   cp config/.env.example config/.env
   
   # Edit the configuration files with your API keys and settings
   # Edit config/config.yaml for model configurations
   # Edit config/.env for API keys
   ```

2. Set up the Minion-Manus project:
   ```bash
   git clone https://github.com/femto/minion-manus.git
   cd minion-manus
   pip install -e .
   ```

3. Set the `MINION_ROOT` environment variable:
   ```bash
   # For bash/zsh (add to your .bashrc or .zshrc)
   export MINION_ROOT=/path/to/minion
   
   # For Windows (set as system environment variable)
   # MINION_ROOT=C:\path\to\minion
   ```
   Replace `/path/to/minion` with the actual path to your Minion installation.

4. Installed the required dependencies:
   ```bash
   pip install nest_asyncio smolagents
   ```

## Overview

The `MinionProviderAdapter` class implements the `Model` interface from SmolaAgents, allowing Minion LLM providers to be used with SmolaAgents' `CodeAgent` and `ToolCallingAgent`. This enables you to use Minion's LLM providers with SmolaAgents' agent capabilities.

## Features

- **Seamless Integration**: Use Minion LLM providers with SmolaAgents without modifying either framework.
- **Synchronous and Asynchronous Support**: The adapter supports both synchronous and asynchronous operations.
- **Tool Integration**: Full support for SmolaAgents' tool system, allowing tools to be used with Minion LLM providers.
- **Error Handling**: Robust error handling to ensure graceful degradation in case of issues.

## Synchronous Implementation

The adapter includes a synchronous implementation of the `__call__` method, which is required by SmolaAgents. This implementation:

1. Uses threading to run the asynchronous `generate` method of the Minion LLM provider in a separate thread.
2. Uses `nest_asyncio` to handle nested event loops, preventing conflicts when the adapter is used in an environment that already has an event loop running.
3. Implements timeout handling to prevent the adapter from hanging indefinitely.
4. Provides detailed error messages in case of failures.

Here's how the synchronous implementation works:

```python
def __call__(self, messages, stop_sequences=None, grammar=None, tools_to_call_from=None, **kwargs):
    # Convert messages and prepare arguments
    minion_messages = self._convert_messages(messages)
    additional_args = {...}  # Prepare additional arguments
    
    # Use a new thread to run the async function
    import threading
    import queue
    result_queue = queue.Queue()
    
    def run_async_in_new_thread():
        import asyncio
        import nest_asyncio
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Apply nest_asyncio to handle nested event loops
        nest_asyncio.apply(loop)
        
        try:
            # Run the async function in the new event loop
            response = loop.run_until_complete(
                self.provider.generate(
                    messages=minion_messages,
                    **additional_args
                )
            )
            result_queue.put(("success", response))
        except Exception as e:
            result_queue.put(("error", str(e)))
        finally:
            loop.close()
    
    # Start the thread and wait for it to complete
    thread = threading.Thread(target=run_async_in_new_thread)
    thread.start()
    thread.join(timeout=30)  # Wait up to 30 seconds
    
    # Process the result and return a ChatMessage
    # ...
```

## Usage Example

Here's a simple example of how to use the adapter:

```python
from minion import config
from minion.providers import create_llm_provider
from smolagents import CodeAgent
from smolagents_adapter import MinionProviderAdapter

# Setup model
model_name = "gpt-4o"
llm_config = config.models.get(model_name)
llm_provider = create_llm_provider(llm_config)

# Create the adapter
llm = MinionProviderAdapter(llm_provider)

# Create a CodeAgent with the adapter
agent = CodeAgent(
    tools=[...],  # Your tools here
    model=llm,
    max_steps=5
)

# Run the agent synchronously
result = agent.run("Your task here")
print(result)

# Or run asynchronously
async def run_async():
    result = await agent.arun("Your async task here")
    print(result)

import asyncio
asyncio.run(run_async())
```

## Message Conversion

The adapter handles the conversion between SmolaAgents' message format and Minion's message format. This includes:

- Converting role names (e.g., "user" to "user", "assistant" to "assistant", etc.)
- Handling multimodal content (text + images)
- Skipping unsupported message types (e.g., "tool-response" messages that require a "name" parameter)

## Tool Integration

The adapter supports SmolaAgents' tool system, allowing tools to be used with Minion LLM providers. This includes:

- Converting tool definitions to the format expected by the Minion LLM provider
- Parsing tool calls from the model's output
- Converting tool responses back to the format expected by SmolaAgents

## Requirements

- `nest_asyncio`: Required for handling nested event loops
- `threading`: Used for running asynchronous code in a separate thread
- `queue`: Used for communication between threads
- Minion framework: The core framework that provides the LLM providers

## Troubleshooting

If you encounter issues with the adapter, here are some common problems and solutions:

- **Timeout Errors**: If the adapter times out, try increasing the timeout value in the `__call__` method.
- **Event Loop Errors**: If you encounter event loop errors, make sure you're using the latest version of `nest_asyncio`.
- **Message Conversion Errors**: If you encounter errors related to message conversion, check the format of the messages you're passing to the adapter.
- **Environment Configuration**: Ensure that the `MINION_ROOT` environment variable is correctly set to the path of your Minion installation.
- **Model Configuration**: Check that your Minion `config.yaml` file has the correct model configurations.

## See Also

- [SmolaAgents Documentation](https://github.com/huggingface/smolagents)
- [Minion Documentation](https://github.com/femto/minion)
- [Full Example](./smolagents_example.py): A complete example of using the adapter with SmolaAgents. 