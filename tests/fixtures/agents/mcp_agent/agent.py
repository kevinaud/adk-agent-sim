"""Test agent with MCP tools for E2E testing.

This agent uses McpToolset to connect to an MCP server, which exercises
the MCP connection handling in the ADK Agent Simulator.
"""

import textwrap

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams


def get_mcp_toolset() -> McpToolset:
  """Create an MCP toolset that connects to a test server.

  Returns:
    McpToolset configured to connect to the test MCP server.
  """
  return McpToolset(
    connection_params=StreamableHTTPConnectionParams(
      url="http://127.0.0.1:9001/mcp",  # Test MCP server port
    ),
  )


def get_mcp_agent() -> Agent:
  """Create a test agent with MCP tools.

  Returns:
    An Agent instance configured with MCP tools for testing.
  """
  return Agent(
    model="gemini-2.5-flash",
    name="mcp_test_agent",
    description="A test agent with MCP tools.",
    instruction=textwrap.dedent("""
    You are a test agent with MCP tools.
    Use the available tools to help the user.
    """),
    tools=[get_mcp_toolset()],
  )


root_agent = get_mcp_agent()
