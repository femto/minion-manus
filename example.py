"""Example usage of Minion Manus."""

import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from minion_manus import MinionAgent, AgentConfig, AgentFramework

# Configure the agent
agent_config = AgentConfig(
    model_id="gpt-4o",  # 使用你的API部署中可用的模型
    name="Research Assistant",
    description="A helpful research assistant",
    instructions="You are a helpful research assistant that can search the web and visit webpages.",
    model_args={"api_key_var": "OPENAI_API_KEY", "base_url_var":"OPENAI_BASE_URL"},  # Will use OPENAI_API_KEY from environment
    agent_type="CodeAgent"  # 指定代理类型
)

async def main():
    try:
        # Create and run the agent
        framework = AgentFramework(
            "smolagents"
        )
        agent = MinionAgent.create(framework, agent_config)
        
        # Run the agent with a question
        # import litellm
        # litellm._turn_on_debug()
        result = agent.run("What are the latest developments in AI?")
        print("Agent's response:", result)
    except Exception as e:
        print(f"Error: {str(e)}")
        # 如果需要调试
        # import litellm
        # litellm._turn_on_debug()
        raise

if __name__ == "__main__":
    asyncio.run(main()) 