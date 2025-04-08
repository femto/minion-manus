#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example demonstrating the use of MinionProviderToSmolAdapter with SmolaAgents.

This example shows how to integrate the Minion provider with SmolaAgents using
our adapter to enable seamless tool calling between the two frameworks.
"""

import os
import sys
import logging
from typing import Dict, Any, List

# Add parent directory to path to import from minion_manus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the adapter first
from minion_manus.providers.adapters import MinionProviderToSmolAdapter

# Import SmolaAgents components
try:
    # Import directly from smolagents.tools to avoid any confusion
    from smolagents.tools import Tool, tool
    from smolagents import ToolCallingAgent, CodeAgent
except ImportError:
    print("SmolaAgents not found. Please install it with: pip install smolagents")
    sys.exit(1)

# Define some simple functions for our tools
def get_current_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location.
    
    Args:
        location: The city to get weather for, e.g. Tokyo, San Francisco
        unit: The temperature unit, either 'celsius' or 'fahrenheit'
        
    Returns:
        A string with the current weather information
    """
    # This is a mock function that would normally call a weather API
    weather_data = {
        "tokyo": {"celsius": 20, "fahrenheit": 68},
        "san francisco": {"celsius": 15, "fahrenheit": 59},
        "paris": {"celsius": 18, "fahrenheit": 64},
        "sydney": {"celsius": 25, "fahrenheit": 77},
    }
    
    location = location.lower()
    if location not in weather_data:
        return f"Weather data for {location} not available."
    
    temperature = weather_data[location][unit.lower()]
    return f"The current weather in {location} is {temperature}° {unit}."

def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate as a string
        
    Returns:
        A string with the calculation result
    """
    try:
        # Use eval safely with only math operations
        # This is just for demonstration purposes
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return f"The result of {expression} is {result}."
    except Exception as e:
        return f"Error calculating: {str(e)}"

def get_capital(country: str) -> str:
    """Get the capital of a country.
    
    Args:
        country: The name of the country to look up
        
    Returns:
        A string with the capital city of the requested country
    """
    capitals = {
        "usa": "Washington, D.C.",
        "united states": "Washington, D.C.",
        "france": "Paris",
        "japan": "Tokyo",
        "australia": "Canberra",
        "brazil": "Brasília",
        "india": "New Delhi",
        "china": "Beijing",
        "uk": "London",
        "united kingdom": "London",
        "germany": "Berlin",
    }
    country = country.lower()
    return capitals.get(country, f"I don't know the capital of {country}.")

def main():
    print("\n=== Minion-Manus with SmolaAgents Example ===")
    
    # Create the Minion adapter
    model_name = "gpt-4o"  # Change to your preferred model
    print(f"\nCreating adapter for {model_name}...")
    
    try:
        adapter = MinionProviderToSmolAdapter.from_model_name(model_name)
        
        # Create our tools using the @tool decorator, which is the preferred way in SmolaAgents
        # This creates a Tool instance automatically
        weather_tool = tool(get_current_weather)
        weather_tool.name = "get_current_weather"
        weather_tool.description = "Get the current weather in a location"
        
        calculate_tool = tool(calculate)
        calculate_tool.name = "calculate"
        calculate_tool.description = "Calculate the result of a mathematical expression"
        
        capital_tool = tool(get_capital)
        capital_tool.name = "get_capital"
        capital_tool.description = "Get the capital city of a country"
        
        # Create a ToolCallingAgent with our adapter and tools
        print("Creating SmolaAgents ToolCallingAgent with Minion provider...")
        agent = CodeAgent(
            tools=[weather_tool, calculate_tool, capital_tool],
            model=adapter,  # Pass our adapter as the model
        )
        
        # Example queries that require tool use
        queries = [
            "What's the weather in Tokyo?",
            #"What's the weather like in Tokyo? And what's the capital of France?",
            # "What is 123 * 456 + 789?",
            # "I need to know the capital of Japan and the current weather in Sydney."
        ]
        
        # Run the agent on each query
        for i, query in enumerate(queries):
            print(f"\n\n=== Example Query {i+1} ===")
            print(f"Query: {query}")
            print("\nRunning agent...")
            try:
                response = agent.run(query)
                print(f"\nResponse: {response}")
            except Exception as e:
                print(f"Error running agent: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n=== Example Completed ===")
    
    except Exception as e:
        print(f"Error setting up the example: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 