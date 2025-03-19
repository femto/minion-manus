#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the MinionProviderToSmolAdapter.

This module tests the functionality of the MinionProviderToSmolAdapter
which converts Minion LLM providers to SmolaAgents compatible models.
"""

import asyncio
import os
import sys
import pytest
from unittest import mock
from typing import List, Dict, Any, Optional

# Add parent directory to path to import from minion_manus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minion_manus.providers.adapters import MinionProviderToSmolAdapter


def test_create_adapter_from_model_name(patch_basic_modules, mock_providers):
    """Test creating adapter directly from model name."""
    adapter = MinionProviderToSmolAdapter(model_name="gpt-4o")
    assert adapter is not None
    
    # Test generate method
    messages = [{"role": "user", "content": "Say hello!"}]
    result = adapter.generate(messages)
    assert result["choices"][0]["message"]["content"] == "Mock response"
    
    # Verify the provider was created with the correct model config
    mock_providers.create_llm_provider.assert_called_once()


def test_create_adapter_from_provider(mock_basic_provider):
    """Test creating adapter from provider."""
    adapter = MinionProviderToSmolAdapter(provider=mock_basic_provider)
    assert adapter is not None
    
    # Test generate method
    messages = [{"role": "user", "content": "What's the weather like today?"}]
    result = adapter.generate(messages)
    assert result["choices"][0]["message"]["content"] == "Mock response"


def test_from_model_name_class_method(patch_basic_modules):
    """Test the from_model_name class method."""
    adapter = MinionProviderToSmolAdapter.from_model_name("gpt-4o")
    assert adapter is not None
    
    # Test generate method
    messages = [{"role": "user", "content": "Tell me a joke."}]
    result = adapter.generate(messages)
    assert result["choices"][0]["message"]["content"] == "Mock response"


@pytest.mark.asyncio
async def test_async_implementation(patch_basic_modules):
    """Test async implementation."""
    adapter = MinionProviderToSmolAdapter.from_model_name("gpt-4o")
    
    # Test agenerate method
    messages = [{"role": "user", "content": "What's your favorite color?"}]
    result = await adapter.agenerate(messages)
    assert result["choices"][0]["message"]["content"] == "Async mock response" 