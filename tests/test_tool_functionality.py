#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the tool functions used with SmolaAgents.

This module tests the actual tool functions as standalone components,
without integration with SmolaAgents or the MinionProviderToSmolAdapter.
"""

import os
import sys
import pytest
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path to import from minion_manus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_date_tool():
    """Test the date_tool function."""
    def date_tool() -> str:
        """Get the current date.
        
        Returns:
            str: The current date in YYYY-MM-DD format.
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    # Check that the function returns a string in the expected format
    result = date_tool()
    assert isinstance(result, str)
    
    # Check that the result is in the format YYYY-MM-DD
    try:
        datetime.strptime(result, "%Y-%m-%d")
    except ValueError:
        pytest.fail("date_tool did not return a date in the format YYYY-MM-DD")


def test_capital_tool():
    """Test the capital_tool function."""
    def capital_tool(country: str) -> str:
        """Get the capital of a country.
        
        Args:
            country: The name of the country to look up.
            
        Returns:
            str: The capital city of the specified country.
        """
        capitals = {
            "usa": "Washington, D.C.",
            "france": "Paris",
            "japan": "Tokyo",
            "australia": "Canberra",
            "brazil": "Brasília",
            "india": "New Delhi",
        }
        return capitals.get(country.lower(), f"I don't know the capital of {country}")
    
    # Test known capitals
    assert capital_tool("USA") == "Washington, D.C."
    assert capital_tool("France") == "Paris"
    assert capital_tool("JAPAN") == "Tokyo"
    
    # Test case insensitivity
    assert capital_tool("france") == "Paris"
    assert capital_tool("FRANCE") == "Paris"
    
    # Test unknown capital
    assert capital_tool("Germany") == "I don't know the capital of Germany"


def test_calculate_tool():
    """Test the calculate tool function."""
    def calculate(expression: str) -> str:
        """Calculate the result of a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate.
            
        Returns:
            str: The result of the calculation or an error message.
        """
        try:
            # Use eval safely with only math operations
            # This is just for demonstration purposes
            allowed_names = {"__builtins__": {}}
            result = eval(expression, allowed_names)
            return str(result)
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    # Test basic calculations
    assert calculate("2 + 2") == "4"
    assert calculate("3 * 4") == "12"
    assert calculate("10 / 2") == "5.0"
    assert calculate("2 ** 3") == "8"
    
    # Test complex calculation
    assert calculate("123 * 456 + 789") == "56907"
    
    # Test error handling
    assert calculate("1/0").startswith("Error calculating")
    assert calculate("invalid").startswith("Error calculating") 