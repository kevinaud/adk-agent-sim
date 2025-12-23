from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")


@mcp.tool
def multiply(a: int, b: int) -> int:
  """Multiplies two numbers."""
  return a * b


def run_server():
  mcp.run(transport="http", port=8001)


if __name__ == "__main__":
  run_server()
