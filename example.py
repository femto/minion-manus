"""Example usage of Minion Manus."""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from minion_manus import MinionAgent, AgentConfig

# Configure the agent
agent_config = AgentConfig(
    model_id="gpt-4.1",  # or your preferred model
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