#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example demonstrating the use of the MinionProviderToSmolAdapter.

This example shows how to use the MinionProviderToSmolAdapter to convert
Minion LLM providers to SmolaAgents compatible models.
"""

import asyncio
import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Add parent directory to path to import from minion_manus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the adapter
from minion_manus.providers.adapters import MinionProviderToSmolAdapter

# Import the patch script
try:
    # Try to apply the patch to the OpenAI provider
    from examples.fix_minion_provider import main as apply_patch
    
    # Apply the patch
    print("\n=== Applying provider patch ===")
    patch_result = apply_patch()
    if patch_result:
        print("Provider patch applied successfully")
    else:
        print("WARNING: Provider patch failed - function messages may not work")
except Exception as e:
    print(f"WARNING: Could not apply provider patch: {e}")
    import traceback
    traceback.print_exc()

# Placeholder functions that will be wrapped as tools
def get_date() -> str:
    """Get the current date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

def get_capital(country: str) -> str:
    """Get the capital of a country."""
    capitals = {
        "usa": "Washington, D.C.",
        "france": "Paris",
        "japan": "Tokyo",
        "australia": "Canberra",
        "brazil": "Brasília",
        "india": "New Delhi",
    }
    return capitals.get(country.lower(), f"I don't know the capital of {country}")

def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        # Use eval safely with only math operations
        # This is just for demonstration purposes
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"

async def main():
    # Demonstrate SmolaAgents integration
    print("\n=== Minion-Manus Adapter Integration ===")
    try:
        # We need a model for this part
        has_model = True
        model_name = "gpt-4o"
        if has_model:
            # Create the adapter
            adapter = MinionProviderToSmolAdapter.from_model_name(model_name)
            
            # Direct adapter usage - without SmolaAgents
            print("\n--- Direct Adapter Usage ---")
            
            # Set up a simple conversation
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is today's date? Also, what is the capital of France?"}
            ]
            
            # Define simple tools
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_date",
                        "description": "Get the current date",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_capital",
                        "description": "Get the capital of a country",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "country": {
                                    "type": "string",
                                    "description": "The country name"
                                }
                            },
                            "required": ["country"]
                        }
                    }
                }
            ]
            
            # Direct call to the adapter
            print("Calling adapter directly with tools...")
            try:
                # Enable debug logging
                import logging
                logging.getLogger('minion_manus').setLevel(logging.INFO)
                
                response = adapter.generate(messages, tools=tools)
                print(f"Response: {response}")
                
                # Handle tool calls if present
                message = response["choices"][0]["message"]
                print(f"\nResponse message: {message}")
                
                if "tool_calls" in message and message["tool_calls"]:
                    print("\nTool calls detected:")
                    for tool_call in message["tool_calls"]:
                        print(f"  Tool: {tool_call['function']['name']}")
                        print(f"  Arguments: {tool_call['function']['arguments']}")
                        
                        # Execute the tool
                        tool_name = tool_call["function"]["name"]
                        tool_args = tool_call["function"]["arguments"]
                        
                        result = None
                        if tool_name == "get_date":
                            result = get_date()
                        elif tool_name == "get_capital":
                            import json
                            args = json.loads(tool_args)
                            result = get_capital(args["country"])
                            
                        # Add tool result to messages
                        if result:
                            print(f"  Result: {result}")
                            
                            # Add tool call to messages
                            tool_call_message = {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [tool_call]
                            }
                            
                            # Create tool response message (Azure format)
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": result
                            }
                            
                            print(f"\nAdding tool call message: {tool_call_message}")
                            messages.append(tool_call_message)
                            
                            print(f"Adding tool response message: {tool_message}")
                            messages.append(tool_message)
                else:
                    print("\nNo tool calls detected in the response.")
                    print("Trying with forced tool choice...")
                    # Try with forced tool choice
                    response = adapter.generate(messages, tools=tools, tool_choice="auto")
                    print(f"Forced tool choice response: {response}")
                    message = response["choices"][0]["message"]
                    print(f"Message with forced tool choice: {message}")
                    
                    if "content" in message and message["content"]:
                        print(f"\nAssistant's response without tools: {message['content']}")
                    
                    if "tool_calls" in message and message["tool_calls"]:
                        print("\nTool calls detected with forced choice:")
                        for tool_call in message["tool_calls"]:
                            print(f"  Tool: {tool_call['function']['name']}")
                            print(f"  Arguments: {tool_call['function']['arguments']}")
                            
                            # Execute the tool
                            tool_name = tool_call["function"]["name"]
                            tool_args = tool_call["function"]["arguments"]
                            
                            result = None
                            if tool_name == "get_date":
                                result = get_date()
                            elif tool_name == "get_capital":
                                import json
                                args = json.loads(tool_args)
                                result = get_capital(args["country"])
                                
                            if result:
                                print(f"  Result: {result}")
                                
                                # Add tool call to messages
                                tool_call_message = {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [tool_call]
                                }
                                
                                # Create tool response message (Azure format)
                                tool_message = {
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "content": result
                                }
                                
                                print(f"\nAdding tool call message: {tool_call_message}")
                                messages.append(tool_call_message)
                                
                                print(f"Adding tool response message: {tool_message}")
                                messages.append(tool_message)
                    
                # Get response with tool results if there are function results
                if any(msg.get("role") == "tool" for msg in messages):
                    print("\nGetting final response with tool results...")
                    final_response = adapter.generate(messages)
                    print(f"Final response: {final_response}")
                    
                    message = final_response["choices"][0]["message"]
                    if "content" in message and message["content"]:
                        print(f"Assistant's final message: {message['content']}")
                else:
                    print("\nNo tool results to process, skipping final response.")
                    except Exception as e:
                print(f"Error with direct adapter usage: {e}")
                import traceback
                traceback.print_exc()
                
            # Try a calculation
            print("\nTesting with calculation...")
            try:
                calc_messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 123 * 456 + 789?"}
                ]
                
                calc_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate",
                            "description": "Calculate a mathematical expression",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "expression": {
                                        "type": "string",
                                        "description": "The mathematical expression to evaluate"
                                    }
                                },
                                "required": ["expression"]
                            }
                        }
                    }
                ]
                
                print("Calling adapter with calculation tools...")
                calc_response = adapter.generate(calc_messages, tools=calc_tools, tool_choice="auto")
                print(f"Calculation response: {calc_response}")
                
                # Handle tool calls if present
                message = calc_response["choices"][0]["message"]
                print(f"\nCalculation message: {message}")
                
                if "tool_calls" in message and message["tool_calls"]:
                    print("\nCalculation tool calls detected:")
                    for tool_call in message["tool_calls"]:
                        print(f"  Tool: {tool_call['function']['name']}")
                        print(f"  Arguments: {tool_call['function']['arguments']}")
                        
                        # Execute the tool
                        tool_name = tool_call["function"]["name"]
                        tool_args = tool_call["function"]["arguments"]
                        
                        result = None
                        if tool_name == "calculate":
                            import json
                            args = json.loads(tool_args)
                            result = calculate(args["expression"])
                            
                        # Add tool result to messages
                        if result:
                            print(f"  Result: {result}")
                            
                            # Add tool call to messages
                            tool_call_message = {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [tool_call]
                            }
                            
                            # Create tool response message (Azure format)
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": result
                            }
                            
                            print(f"\nAdding tool call message: {tool_call_message}")
                            calc_messages.append(tool_call_message)
                            
                            print(f"Adding tool response message: {tool_message}")
                            calc_messages.append(tool_message)
                            
                            # Get final response with calculation result
                            print("\nGetting final calculation response...")
                            final_calc_response = adapter.generate(calc_messages)
                            print(f"Final calculation response object: {final_calc_response}")
                            
                            message = final_calc_response["choices"][0]["message"]
                            if "content" in message and message["content"]:
                                print(f"Final calculation message: {message['content']}")
                else:
                    print("No calculation tool calls detected in the response.")
            except Exception as e:
                print(f"Error with calculation: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Skipping integration - no models available")
    except Exception as e:
        print(f"Error setting up integration: {e}")
        import traceback
        traceback.print_exc()

    print("\nExample completed.")

if __name__ == "__main__":
    asyncio.run(main()) 