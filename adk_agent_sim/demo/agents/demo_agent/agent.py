import textwrap

from google.adk.agents.llm_agent import Agent
<<<<<<< HEAD
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams


def add(a: int, b: int) -> int:
  """Adds two numbers."""
  return a + b


def get_demo_function_tool() -> FunctionTool:
  return FunctionTool(add)

<<<<<<< HEAD

=======
>>>>>>> 55ecd18 (save)
def get_demo_mcp_server_toolset() -> McpToolset:
  return McpToolset(
    connection_params=StreamableHTTPConnectionParams(
=======
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams


def get_demo_server_toolset() -> McpToolset:
  return McpToolset(
    connection_params=SseConnectionParams(
>>>>>>> 24c0978 (save)
      url="http://127.0.0.1:8001/mcp",
    ),
  )


def get_demo_agent() -> Agent:
  return Agent(
    model="gemini-2.5-flash",
    name="calculator_agent",
    description="A helpful assistant for performing mathematical calculations.",
    instruction=textwrap.dedent("""
    You are an expert mathematician.
    
<<<<<<< HEAD
    Use the available MCP tools to perform requested calculations accurately and
    efficiently.
"""),
<<<<<<< HEAD
    tools=[get_demo_function_tool(), get_demo_mcp_server_toolset()],
=======
    tools=[get_demo_function_tool(), get_demo_mcp_server_toolset()]
>>>>>>> 55ecd18 (save)
=======
    Use the available MCP tools to perform requested calculations accurately and efficiently.
"""),
    tools=[get_demo_server_toolset()]
>>>>>>> 24c0978 (save)
  )


root_agent = get_demo_agent()
