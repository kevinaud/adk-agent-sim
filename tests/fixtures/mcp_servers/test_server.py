"""Test MCP server for E2E testing."""

from fastmcp import FastMCP

mcp = FastMCP("Test MCP Server")


@mcp.tool
def echo(message: str) -> str:
  """Echo the input message back.

  Args:
    message: The message to echo.

  Returns:
    The same message that was input.
  """
  return f"Echo: {message}"


@mcp.tool
def multiply(a: int, b: int) -> int:
  """Multiply two numbers together.

  Args:
    a: First number.
    b: Second number.

  Returns:
    The product of a and b.
  """
  return a * b


def run_server(port: int = 9001) -> None:
  """Run the MCP server on the specified port.

  Args:
    port: The port to run the server on.
  """
  mcp.run(transport="http", port=port)


if __name__ == "__main__":
  run_server()
