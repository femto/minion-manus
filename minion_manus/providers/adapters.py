"""
Provider adapters for Minion-Manus.

This module contains adapters for using Minion LLM providers with external frameworks.
"""

import asyncio
import inspect
import threading
import logging
import time
from typing import Any, Dict, List, Optional, Union

import nest_asyncio
from smolagents.models import get_tool_json_schema, ChatMessage, parse_tool_args_if_needed, get_clean_message_list, \
    tool_role_conversions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to apply nest_asyncio to handle event loop conflicts in sync mode
try:
    nest_asyncio.apply()
except Exception:
    pass


class BaseSmolaAgentsModelAdapter:
    """
    Base class for adapting providers to SmolaAgents models interface.
    
    This abstract class defines the interface needed for SmolaAgents compatibility.
    """
    
    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a response synchronously.
        
        Args:
            messages: List of messages in SmolaAgents format
            tools: Optional list of tools to use
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            Response in SmolaAgents format
        """
        raise NotImplementedError("Subclasses must implement generate method")
    
    async def agenerate(self, messages: List[Dict[str, Any]], tools: Optional[List] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a response asynchronously.
        
        Args:
            messages: List of messages in SmolaAgents format
            tools: Optional list of tools to use
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            Response in SmolaAgents format
        """
        raise NotImplementedError("Subclasses must implement agenerate method")
    
    def __call__(self, messages: List[Dict[str, Any]], stop_sequences: Optional[List[str]] = None, grammar=None, **kwargs) -> ChatMessage:
        """
        Call interface required by SmolaAgents.
        
        Args:
            messages: List of messages
            stop_sequences: Optional list of sequences to stop generation
            grammar: Optional grammar for constrained generation
            **kwargs: Additional arguments
            
        Returns:
            SmolaAgents ChatMessage object
        """
        # Convert stop_sequences to use with the provider
        messages = get_clean_message_list(
            messages,
            role_conversions=tool_role_conversions,
            convert_images_to_image_urls=True,
            flatten_messages_as_text=False,
        )
        if stop_sequences:
            kwargs["stop"] = stop_sequences
        
        # Extract tools if present and convert them
        tools = kwargs.pop("tools", None)
        
        # Handle tools_to_call_from parameter from newer SmolaAgents versions
        tools_to_call_from = kwargs.pop("tools_to_call_from", None)
        if tools_to_call_from and not tools:
            tools = tools_to_call_from
            kwargs["tool_choice"] = "auto"  # Signal that we want to use tools
        
        if tools:
            tools = self._convert_tools_for_smolagents(tools)
            
        # Call generate and extract message from the response
        chat_message = self.generate(messages, tools=tools, **kwargs)
        
        return chat_message

class MinionProviderToSmolAdapter(BaseSmolaAgentsModelAdapter):
    """
    Adapter for using Minion LLM providers with SmolaAgents.
    
    This adapter wraps a Minion LLM provider and exposes the interface 
    expected by SmolaAgents (generate and agenerate methods).
    
    It supports both synchronous and asynchronous operations.
    """
    
    def __init__(self, provider=None, model_name="default", async_api=True):
        """
        Initialize the adapter with a Minion LLM provider.
        
        Args:
            provider: A Minion LLM provider instance. If None, model_name must be provided.
            model_name: Name of the model to use in minion config. If provided, provider will be created.
            async_api: Whether the provider supports async API
        """
        if provider is None and model_name is None:
            raise ValueError("Either provider or model_name must be provided")
            
        self.provider = provider
        self.supports_async = async_api
        
        # Create provider from model_name if needed
        if provider is None and model_name is not None:
            try:
                from minion import config
                from minion.providers import create_llm_provider
                
                llm_config = config.models.get(model_name)
                if llm_config is None:
                    raise ValueError(f"Model {model_name} not found in minion config")
                    
                self.provider = create_llm_provider(llm_config)
            except ImportError:
                raise ImportError("Minion framework not installed. Please install minion first.")
    
    @classmethod
    def from_model_name(cls, model_name, async_api=True):
        """
        Create an adapter from a model name in minion config.
        
        Args:
            model_name: The model name to use from minion config
            async_api: Whether the provider supports async API
            
        Returns:
            MinionProviderToSmolAdapter instance
        """
        return cls(model_name=model_name, async_api=async_api)
        
    def _convert_messages(self, messages):
        """
        Convert SmolaAgents messages to Minion format.
        
        Args:
            messages: List of SmolaAgents messages
            
        Returns:
            List of messages in Minion format
        """
        # If we have the Message class, try to use it
        # Otherwise use dictionary format
        return self._convert_to_dicts(messages)
    
    def _convert_to_dicts(self, messages):
        """
        Convert messages to dictionary format.
        
        Args:
            messages: List of messages in SmolaAgents format
            
        Returns:
            List of message dictionaries
        """
        converted_messages = [self._create_message_dict(msg) for msg in messages]
        
        # Ensure all function messages have a name
        for msg in converted_messages:
            if msg.get("role") == "function" and "name" not in msg:
                msg["name"] = "function_call"
                logger.warning(f"Adding missing 'name' field to function message: {msg}")
        
        return converted_messages
    
    def _create_message_dict(self, msg):
        """
        Create a message dictionary from a SmolaAgents message.
        
        Args:
            msg: A message in SmolaAgents format
            
        Returns:
            A message dictionary for Minion
        """
        role = msg.get("role", "")
        
        # Handle special roles - convert to supported roles
        needs_name = False
        if role == "tool-response":
            role = "function"  # Convert to function which is supported
            needs_name = True
        
        # All function messages need a name
        if role == "function":
            needs_name = True
        
        # Handle content which could be a string or a list of content blocks
        content = msg.get("content", "")
        if content is None:
            # Replace None with empty string to avoid validation errors
            content = ""
        elif isinstance(content, list):
            # Extract text from content blocks
            text_parts = []
            for block in content:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = " ".join(text_parts)
        
        # Create dictionary with appropriate attributes
        minion_msg = {
            "role": role,
            "content": content
        }
        
        # Add tool calls if present
        if "tool_calls" in msg:
            minion_msg["tool_calls"] = msg["tool_calls"]
            
        # Add tool call id if present
        if "tool_call_id" in msg:
            minion_msg["tool_call_id"] = msg["tool_call_id"]
            
        # Add name if present or required
        if "name" in msg:
            minion_msg["name"] = msg["name"]
        elif needs_name:
            # When role is function (or converted from tool-response), name is required
            # For function roles, use name from message or default to function_call
            if role == "function" and "name" not in minion_msg:
                default_name = "function_call"
                # Try to extract name from tool_call_id if available
                if "tool_call_id" in msg:
                    default_name = f"function_for_{msg['tool_call_id']}"
                minion_msg["name"] = default_name
            else:
                minion_msg["name"] = msg.get("name", "tool_response")
            
        return minion_msg
    
    def _convert_tools(self, tools):
        """
        Convert SmolaAgents tools to Minion format.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Tools in Minion format
        """
        if not tools:
            return None
            
        # First, ensure tools are in the OpenAI function calling format
        openai_tools = self._convert_tools_for_smolagents(tools)
        
        # In most cases, the OpenAI format is compatible with Minion
        # but we might need to enhance this in the future
        return openai_tools
    
    def _run_async_in_thread(self, coro, *args, **kwargs):
        """
        Run an async coroutine in a separate thread.
        
        This allows calling async methods from synchronous code.
        
        Args:
            coro: The async coroutine to run
            *args: Arguments to pass to the coroutine
            **kwargs: Keyword arguments to pass to the coroutine
            
        Returns:
            The result of the coroutine
        """
        result_container = []
        error_container = []
        
        def thread_target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(coro(*args, **kwargs))
                result_container.append(result)
            except Exception as e:
                error_container.append(e)
            finally:
                loop.close()
        
        thread = threading.Thread(target=thread_target)
        thread.start()
        thread.join()
        
        if error_container:
            raise error_container[0]
            
        return result_container[0]
    
    def flat_dict_messages(self, messages):
        """
        Convert Message objects or dictionaries to flat API-compatible dictionaries.
        
        Args:
            messages: List of Message objects or dictionaries
            
        Returns:
            List of flat dictionaries for API calls
        """
        flat_messages = []
        
        for msg in messages:
            if hasattr(msg, 'model_dump'):
                # Handle Pydantic model objects
                model_dict = msg.model_dump()
                flat_dict = {"role": model_dict["role"]}
                
                # Extract text content from nested content structure
                if "content" in model_dict:
                    if isinstance(model_dict["content"], dict) and "text" in model_dict["content"]:
                        flat_dict["content"] = model_dict["content"]["text"]
                    else:
                        flat_dict["content"] = model_dict["content"]
                
                # Add name field if present (required for function/tool roles)
                if "name" in model_dict and model_dict["name"]:
                    flat_dict["name"] = model_dict["name"]
                # Ensure function messages always have name
                elif model_dict["role"] == "function" or model_dict["role"] == "tool":
                    flat_dict["name"] = model_dict.get("name", "function_call")
                    logger.warning(f"Adding missing name 'function_call' to function message with role {model_dict['role']}")
                    
                # Copy tool_calls field if present
                if "tool_calls" in model_dict and model_dict["tool_calls"]:
                    flat_dict["tool_calls"] = model_dict["tool_calls"]
                
                # Copy tool_call_id field if present
                if "tool_call_id" in model_dict and model_dict["tool_call_id"]:
                    flat_dict["tool_call_id"] = model_dict["tool_call_id"]
                    
                flat_messages.append(flat_dict)
            elif isinstance(msg, dict):
                # For dictionaries, ensure they're flat
                flat_dict = {"role": msg["role"]}
                
                if "content" in msg:
                    if isinstance(msg["content"], dict) and "text" in msg["content"]:
                        flat_dict["content"] = msg["content"]["text"]
                    else:
                        flat_dict["content"] = msg["content"]
                
                # Copy name field if present
                if "name" in msg and msg["name"]:
                    flat_dict["name"] = msg["name"]
                # Ensure function messages always have name
                elif msg["role"] == "function" or msg["role"] == "tool":
                    flat_dict["name"] = "function_call"
                    logger.warning(f"Adding missing name 'function_call' to dict function message with role {msg['role']}")
                
                # Copy tool_calls field if present
                if "tool_calls" in msg and msg["tool_calls"]:
                    flat_dict["tool_calls"] = msg["tool_calls"]
                
                # Copy tool_call_id field if present
                if "tool_call_id" in msg and msg["tool_call_id"]:
                    flat_dict["tool_call_id"] = msg["tool_call_id"]
                    
                flat_messages.append(flat_dict)
            else:
                # Handle any other case
                flat_dict = None
                if hasattr(msg, 'role'):
                    # It's an object with attributes
                    flat_dict = {"role": msg.role}
                    
                    # Add content field
                    if hasattr(msg, 'content'):
                        if hasattr(msg.content, 'text'):
                            flat_dict["content"] = msg.content.text
                        else:
                            flat_dict["content"] = msg.content
                            
                    # Handle name for function messages - CRITICAL
                    if hasattr(msg, 'name') and msg.name:
                        flat_dict["name"] = msg.name
                    elif msg.role == "function" or msg.role == "tool":
                        flat_dict["name"] = "function_call"
                        logger.warning(f"Adding missing name 'function_call' to object function message")
                    
                    # Handle tool calls
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        flat_dict["tool_calls"] = msg.tool_calls
                        
                    # Handle tool call id
                    if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                        flat_dict["tool_call_id"] = msg.tool_call_id
                
                if flat_dict:
                    flat_messages.append(flat_dict)
                else:
                    # Last resort: just add as is
                    flat_messages.append(msg)
                
        # Debug: log the flat messages with emphasis on function messages
        for i, msg in enumerate(flat_messages):
            role = msg.get("role", "unknown")
            if role in ["function", "tool"]:
                logger.debug(f"Flat message {i}: {msg}")
                if "name" not in msg:
                    logger.error(f"CRITICAL ERROR: Flat message {i} has role '{role}' but no 'name' field after processing")
        
        return flat_messages
    def _construct_response_from_text(self, text):
        raise NotImplementedError("NotImplementedError")

    async def agenerate(self, messages: List[Dict[str, Any]], tools: Optional[List] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a response asynchronously using the Minion provider.
        
        Args:
            messages: List of messages in SmolaAgents format
            tools: Optional list of tools to use
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            Response in SmolaAgents format
        """
        # Convert messages to Minion format
        minion_messages = self._convert_messages(messages)
        
        # Also prepare flat dictionaries for API compatibility
        flat_messages = self.flat_dict_messages(minion_messages)
        
        # Extract parameters that might be relevant for the provider
        temperature = kwargs.pop("temperature", None)
        stop_sequences = kwargs.pop("stop", None)
        
        # Check if a tool call was requested by the last message
        tools_requested = False
        if tools and isinstance(tools, list) and len(tools) > 0:
            tools_requested = True
            logger.info(f"Tool call was requested with {len(tools)} tools")
        
        # Add tools in kwargs if provided
        if tools:
            # Convert to OpenAI format first to ensure compatibility
            openai_tools = self._convert_tools_for_smolagents(tools)
            kwargs["tools"] = openai_tools
        
        # Add stop sequences if provided
        if stop_sequences:
            kwargs["stop"] = stop_sequences
            
        try:
            # Call the Minion provider
            # Check if provider has generate_sync method (new style)
            if hasattr(self.provider, "generate_sync"):
                # Call generate_sync method directly
                logger.info("Using provider.generate_sync method (async context)")
                
                # Always use patched flat dictionaries
                logger.info("Using patched flat dictionaries with provider (async)")
                patched_messages = []
                for msg in flat_messages:
                    if isinstance(msg, dict):
                        class DictWithAttrs(dict):
                            def __getattr__(self, name):
                                if name in self:
                                    return self[name]
                                raise AttributeError(f"'DictWithAttrs' object has no attribute '{name}'")
                        patched_msg = DictWithAttrs(msg)
                        patched_messages.append(patched_msg)
                    else:
                        patched_messages.append(msg)
                        
                try:
                    # We're in an async context but want to call sync method
                    # Run in a separate thread to avoid blocking
                    loop = asyncio.get_event_loop()
                    text = await loop.run_in_executor(
                        None,
                        lambda: self.provider.generate_sync(
                        messages=patched_messages,
                        temperature=temperature,
                        **kwargs
                        )
                    )
                    return self._construct_response_from_text(text)
                except Exception as e:
                    logger.error(f"Error in async generate_sync: {e}")
                    return self._construct_response_from_text(f"Error: {str(e)}")
            
            # Fallback to achat_completion method (old style)
            elif hasattr(self.provider, "achat_completion"):
                logger.info("Using provider.achat_completion method")
                try:
                    # Try with Message objects first
                    all_message_objects = all(hasattr(msg, 'model_dump') for msg in minion_messages)
                    if all_message_objects:
                        logger.info("Using Message objects directly with provider (achat_completion)")
                        response = await self.provider.achat_completion(
                            messages=minion_messages,
                            temperature=temperature,
                            **kwargs
                        )
                    else:
                        # Fall back to patched dictionaries
                        logger.info("Using patched dictionaries with provider (achat_completion)")
                        patched_messages = []
                        for msg in flat_messages:
                            if isinstance(msg, dict):
                                class DictWithAttrs(dict):
                                    def __getattr__(self, name):
                                        if name in self:
                                            return self[name]
                                        raise AttributeError(f"'DictWithAttrs' object has no attribute '{name}'")
                                patched_msg = DictWithAttrs(msg)
                                patched_messages.append(patched_msg)
                            else:
                                patched_messages.append(msg)
                                
                        response = await self.provider.achat_completion(
                            messages=patched_messages,
                            temperature=temperature,
                            **kwargs
                        )
                    return response
                except Exception as e:
                    logger.error(f"Error in achat_completion: {e}")
                    return self._construct_response_from_text(f"Error: {str(e)}")
            
            # Last resort: call chat_completion synchronously
            else:
                logger.info("Using provider.chat_completion method (sync in async)")
                response = self.provider.chat_completion(
                    messages=flat_messages,
                    temperature=temperature,
                    **kwargs
                )
                return response
        except Exception as e:
            logger.error(f"Error in agenerate: {e}")
            # Return a minimal response with the error message
            return self._construct_response_from_text(f"Error: {str(e)}")
    
    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a response synchronously using the Minion provider.
        
        This method handles both providers with sync APIs and async APIs through threads.
        
        Args:
            messages: List of messages in SmolaAgents format
            tools: Optional list of tools to use
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            Response in SmolaAgents format
        """
        # Debug: Log input messages 
        for i, msg in enumerate(messages):
            logger.debug(f"Input message {i}: {msg}")
            if msg.get("role") == "function" and "name" not in msg:
                logger.warning(f"Input message {i} has role 'function' but no 'name' field")
        
        # If provider has async API only, use thread to run async method
        if self.supports_async and not hasattr(self.provider, "generate_sync"):
            logger.info("Provider has only async API, using thread to run async method")
            try:
                # Check if we're in an event loop
                asyncio.get_event_loop()
                # If we are, we can use asyncio.run
                return self._run_async_in_thread(self.agenerate, messages, tools, **kwargs)
            except RuntimeError:
                # No event loop, use thread method
                return self._run_async_in_thread(self.agenerate, messages, tools, **kwargs)
        
        try:
            # Convert messages to Minion format
            minion_messages = self._convert_messages(messages)
            
            # Also prepare flat dictionaries for API compatibility
            flat_messages = self.flat_dict_messages(minion_messages)
            
            # Extract parameters that might be relevant for the provider
            temperature = kwargs.pop("temperature", None)
            stop_sequences = kwargs.pop("stop", None)
            
            # Check if a tool call was requested by the last message
            tools_requested = False
            if tools and isinstance(tools, list) and len(tools) > 0:
                tools_requested = True
                logger.info(f"Tool call was requested with {len(tools)} tools")
            
            # Add tools in kwargs if provided
            if tools:
                # Convert to OpenAI format first to ensure compatibility
                #openai_tools = self._convert_tools_for_smolagents(tools)
                kwargs["tools"] = tools
            
            # Add stop sequences if provided
            if stop_sequences:
                kwargs["stop"] = stop_sequences
            
            # Check which API the provider supports - prioritize generate_sync
            if hasattr(self.provider, "generate_sync_raw"):
                # Synchronous generate method
                logger.info("Using provider.generate_sync_raw method")
                
                try:
                    response = self.provider.generate_sync_raw(
                        messages=flat_messages,
                        temperature=temperature,
                        **kwargs
                    )

                    # self.last_input_token_count = response.usage.prompt_tokens
                    # self.last_output_token_count = response.usage.completion_tokens

                    message = ChatMessage.from_dict(
                        response.choices[0].message.model_dump(include={"role", "content", "tool_calls"})
                    )
                    message.raw = response
                    if tools is not None:
                        return parse_tool_args_if_needed(message)
                    return message
                except Exception as e:
                    logger.error(f"Error in generate_sync: {e}")
                    raise e
            
            # No sync API available, use async in thread
            else:
                logger.info("No sync API available, using async in thread")
                return self._run_async_in_thread(self.agenerate, messages, tools, **kwargs)
        except Exception as e:
            logger.error(f"Error in generate: {e}")
            # Return a minimal response with the error message
            raise e
            
    def _convert_tools_for_smolagents(self, tools):
        """
        Convert tools for use with SmolaAgents.
        
        This method ensures tools are in the format expected by SmolaAgents.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Tools in SmolaAgents format
        """
        if not tools:
            return None
            
        # Ensure tools are in the expected format for SmolaAgents
        # SmolaAgents expects tools to be instances of smolagents.Tool
        # or dictionaries with the OpenAI function calling format
        formatted_tools = [get_tool_json_schema(tool) for tool in tools]

        logger.debug(f"Converted {len(tools)} tools to {len(formatted_tools)} formatted tools")
        return formatted_tools 