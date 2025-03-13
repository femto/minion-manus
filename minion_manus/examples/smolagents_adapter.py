#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Adapter module to make minion LLM providers compatible with smolagents Model interface.

@Time    : 2024/7/15 10:00
@Author  : femto Zheng
@File    : smolagents_adapter.py
"""
import asyncio
import json
from typing import List, Dict, Optional, Any, Union

from smolagents.models import Model, ChatMessage, ChatMessageToolCall, ChatMessageToolCallDefinition, MessageRole
from smolagents.tools import Tool
from minion.message_types import Message


class MinionProviderAdapter(Model):
    """
    Adapter class that makes minion LLM providers compatible with smolagents Model interface.
    
    This adapter wraps a minion LLM provider and implements the __call__ method expected by smolagents.
    
    Parameters:
        provider: A minion LLM provider instance
        **kwargs: Additional keyword arguments to pass to the provider
    """
    
    def __init__(self, provider, **kwargs):
        super().__init__(**kwargs)
        self.provider = provider
        self.last_input_token_count = None
        self.last_output_token_count = None
    
    def _convert_role(self, role: str) -> str:
        """Convert smolagents MessageRole to minion MessageRole"""
        role_mapping = {
            MessageRole.USER: "user",
            MessageRole.ASSISTANT: "assistant",
            MessageRole.SYSTEM: "system",
            "user": "user",
            "assistant": "assistant",
            "system": "system",
        }
        return role_mapping.get(role, role)
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Message]:
        """Convert smolagents messages to minion Message objects"""
        minion_messages = []
        
        for message in messages:
            # Convert role names to ones supported by the OpenAI API
            role = message["role"]
            content = message["content"]
            
            # Skip tool-response messages since they require a name parameter
            # which is not supported by the Message class
            if role == "tool-response":
                continue
            
            if role == "tool-call":
                role = "assistant"  # Convert tool-call to assistant
            else:
                role = self._convert_role(role)
            
            # Handle different content formats
            if isinstance(content, list):
                # Handle multimodal content (text + images)
                text_content = ""
                for item in content:
                    if item["type"] == "text":
                        text_content += item["text"]
                minion_messages.append(Message(role=role, content=text_content))
            else:
                # Handle text-only content
                minion_messages.append(Message(role=role, content=content))
        
        return minion_messages
    
    def _parse_tool_call(self, content: str) -> Optional[ChatMessageToolCall]:
        """Parse tool call from the model output"""
        try:
            # Try to find JSON structure in the content
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx+1]
                tool_data = json.loads(json_str)
                
                # Extract tool name and arguments
                tool_name = tool_data.get("action") or tool_data.get("name")
                tool_args = tool_data.get("action_input") or tool_data.get("arguments")
                
                if tool_name:
                    return ChatMessageToolCall(
                        id=f"call_{hash(content) % 10000}",
                        type="function",
                        function=ChatMessageToolCallDefinition(
                            name=tool_name,
                            arguments=tool_args
                        )
                    )
        except Exception:
            pass
        
        return None
    
    async def _async_call(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs
    ) -> ChatMessage:
        """Async implementation of the call method"""
        minion_messages = self._convert_messages(messages)
        
        # Prepare additional arguments
        additional_args = {}
        if stop_sequences:
            additional_args["stop"] = stop_sequences
        
        # Add tools information if provided
        if tools_to_call_from:
            tools_info = []
            for tool in tools_to_call_from:
                tools_info.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": tool.inputs,
                            "required": [k for k in tool.inputs.keys()]
                        }
                    }
                })
            additional_args["tools"] = tools_info
            additional_args["tool_choice"] = "auto"
        
        # Add any other kwargs
        additional_args.update(kwargs)
        
        # Generate response using the provider
        response = await self.provider.generate(
            messages=minion_messages,
            **additional_args
        )
        
        # Create ChatMessage from the response
        tool_calls = None
        if tools_to_call_from:
            tool_call = self._parse_tool_call(response)
            if tool_call:
                tool_calls = [tool_call]
        
        return ChatMessage(
            role="assistant",
            content=response,
            tool_calls=tool_calls,
            raw={"response": response}
        )
    
    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs
    ) -> ChatMessage:
        """
        Process the input messages and return the model's response.
        
        This method implements the interface expected by smolagents.
        
        Parameters:
            messages: A list of message dictionaries to be processed
            stop_sequences: A list of strings that will stop generation if encountered
            grammar: The grammar or formatting structure to use (not used in this adapter)
            tools_to_call_from: A list of tools that the model can use
            **kwargs: Additional keyword arguments to pass to the provider
            
        Returns:
            ChatMessage: A chat message object containing the model's response
        """
        try:
            # Convert smolagents messages to minion Message objects
            minion_messages = self._convert_messages(messages)
            
            # Prepare additional arguments
            additional_args = {}
            if stop_sequences:
                additional_args["stop"] = stop_sequences
            
            # Add tools information if provided
            if tools_to_call_from:
                tools_info = []
                for tool in tools_to_call_from:
                    tools_info.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": "object",
                                "properties": tool.inputs,
                                "required": [k for k in tool.inputs.keys()]
                            }
                        }
                    })
                additional_args["tools"] = tools_info
                additional_args["tool_choice"] = "auto"
            
            # Add any other kwargs
            additional_args.update(kwargs)
            
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
            
            if thread.is_alive():
                # If the thread is still running after timeout, return a timeout error
                return ChatMessage(
                    role="assistant",
                    content="Error: Request timed out after 30 seconds",
                    tool_calls=None,
                    raw={"error": "timeout"}
                )
            
            # Get the result from the queue
            result_type, result_value = result_queue.get()
            
            if result_type == "error":
                return ChatMessage(
                    role="assistant",
                    content=f"Error in generating response: {result_value}",
                    tool_calls=None,
                    raw={"error": result_value}
                )
            
            # Process the successful response
            response = result_value
            
            # Create ChatMessage from the response
            tool_calls = None
            if tools_to_call_from:
                tool_call = self._parse_tool_call(response)
                if tool_call:
                    tool_calls = [tool_call]
            
            return ChatMessage(
                role="assistant",
                content=response,
                tool_calls=tool_calls,
                raw={"response": response}
            )
        except Exception as e:
            # If there's an error, return a simple response
            return ChatMessage(
                role="assistant",
                content=f"Error in generating response: {str(e)}",
                tool_calls=None,
                raw={"error": str(e)}
            ) 