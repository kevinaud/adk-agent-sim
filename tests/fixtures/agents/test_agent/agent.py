"""Test agent with diverse FunctionTools for E2E testing.

This agent is specifically designed to exercise different UI widget types
and error handling scenarios in the ADK Agent Simulator E2E tests.
"""

import textwrap
from typing import Literal

from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool


def add_numbers(a: int, b: int) -> int:
  """Add two numbers together.

  Args:
    a: The first number to add.
    b: The second number to add.

  Returns:
    The sum of a and b.
  """
  return a + b


def greet(name: str, formal: bool) -> str:
  """Generate a greeting for a person.

  Args:
    name: The name of the person to greet.
    formal: Whether to use a formal greeting style.

  Returns:
    A personalized greeting message.
  """
  if formal:
    return f"Good day, {name}. It is a pleasure to meet you."
  return f"Hey {name}! Nice to meet you!"


def get_status(level: Literal["low", "medium", "high"]) -> str:
  """Get a status message based on the specified level.

  Args:
    level: The priority level (low, medium, or high).

  Returns:
    A markdown-formatted status message corresponding to the level.
  """
  messages = {
    "low": (
      "## Status: All Systems Nominal\n\n"
      "**No action required.**\n\n"
      "- System healthy\n"
      "- Resources available"
    ),
    "medium": (
      "## Status: Attention Needed\n\n"
      "**Please review** the following items:\n\n"
      "1. Check logs\n"
      "2. Review alerts"
    ),
    "high": (
      "## Status: URGENT\n\n"
      "**Immediate action required!**\n\n"
      "- Critical alert active\n"
      "- [View Dashboard](http://example.com)"
    ),
  }
  return messages[level]


def get_user_info(user_id: int) -> str:
  """Get user information as JSON text.

  This tool returns structured data as a JSON string for testing
  the presentation toggle functionality (Raw/JSON/Markdown modes).

  Args:
    user_id: The user ID to look up.

  Returns:
    JSON string containing user information.
  """
  import json

  user_data = {
    "id": user_id,
    "name": "Test User",
    "email": f"user{user_id}@example.com",
    "roles": ["admin", "user"],
    "settings": {"theme": "dark", "notifications": True},
  }
  return json.dumps(user_data, indent=2)


def fail_always() -> str:
  """A tool that always fails with an error.

  This tool is intentionally designed to raise an exception for testing
  the error handling capabilities of the simulator UI.

  Returns:
    Never returns - always raises RuntimeError.

  Raises:
    RuntimeError: Always raised to test error handling.
  """
  raise RuntimeError("This tool intentionally fails for testing purposes.")


def get_test_agent() -> Agent:
  """Create and return the test agent with all FunctionTools.

  Returns:
    An Agent instance configured with diverse tools for E2E testing.
  """
  return Agent(
    model="gemini-2.5-flash",
    name="TestAgent",
    description="Agent with diverse tools for E2E testing",
    instruction=textwrap.dedent("""
      You are a test agent used for E2E testing of the ADK Agent Simulator.
      
      You have access to several tools:
      - add_numbers: Add two integers together
      - greet: Generate a greeting (with formal/informal option)
      - get_status: Get a status message by priority level
      - get_user_info: Get user data as JSON text
      - fail_always: A tool that always fails (for error testing)
      
      Use these tools as requested by the user.
    """),
    tools=[
      FunctionTool(add_numbers),
      FunctionTool(greet),
      FunctionTool(get_status),
      FunctionTool(get_user_info),
      FunctionTool(fail_always),
    ],
  )


root_agent = get_test_agent()
