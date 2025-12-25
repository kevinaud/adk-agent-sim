"""
Example queries:
- "Which products are currently out of stock?" (Answer: Mechanical Keyboard)
- "How much has Alice Engineer spent in total?" (Requires joining/aggregating data)
- "Does Charlie have any pending orders?" (Answer: No, he has no orders)
"""

import os
import shutil
import textwrap

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
  StdioConnectionParams,
  StdioServerParameters,
)


def get_sqlite_mcp_toolset() -> McpToolset:
  # Locate the mcp-server-sqlite binary in the path (provided by uv/venv)
  executable = shutil.which("mcp-server-sqlite")
  if not executable:
    raise FileNotFoundError(
      "Could not find 'mcp-server-sqlite'. "
      "Did you run 'uv add --dev mcp-server-sqlite'?"
    )

  # Resolve the DB path relative to this file
  db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.db")

  return McpToolset(
    connection_params=StdioConnectionParams(
      server_params=StdioServerParameters(
        command=executable,
        args=[
          "--db-path",
          db_path,
        ],
      )
    ),
  )


def get_sqlite_agent() -> Agent:
  return Agent(
    model="gemini-2.5-flash",
    name="sqlite_agent",
    description="A helper agent for inspecting and querying SQLite databases.",
    instruction=textwrap.dedent("""
        You are a helpful database assistant.
        
        Use the available MCP tools to inspect schemas and query the SQLite database
        efficiently. Always verify table names (e.g., using list_tables) 
        before attempting to query them.
    """),
    tools=[get_sqlite_mcp_toolset()],
  )
