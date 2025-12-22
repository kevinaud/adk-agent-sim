# Research: ADK Agent Simulator Integration

**Feature**: 001-core-agent-simulator  
**Date**: 2025-12-22

## ADK Library Investigation

### Agent Introspection API

The Google ADK provides several methods for inspecting agent configuration:

#### `agent.canonical_tools()`
- **Returns**: `list[BaseTool]` - All tools attached to the agent
- **Async**: Yes, must be awaited
- **Usage**: Primary discovery method for enumerating available tools

#### `agent.canonical_instruction()`
- **Returns**: `str` - The system instruction/prompt for the agent
- **Async**: No
- **Usage**: Display agent persona/context to human simulator

#### Agent Metadata
- `agent.name` - Agent identifier
- `agent.description` - Human-readable description

### Tool Schema API

#### `tool._get_declaration()`
- **Returns**: `FunctionDeclaration` (Gemini API type)
- **Note**: Private API (underscore prefix), may change between versions
- **Structure**:
  ```python
  FunctionDeclaration(
      name="tool_name",
      description="Tool description",
      parameters=Schema(
          type=Type.OBJECT,
          properties={
              "param1": Schema(type=Type.STRING, description="..."),
              "param2": Schema(type=Type.INTEGER, description="..."),
          },
          required=["param1"]
      )
  )
  ```

### Tool Execution API

#### `tool.run_async(args, tool_context)`
- **Parameters**:
  - `args`: Dict of argument name → value
  - `tool_context`: `ToolContext` instance
- **Returns**: Tool-specific output (varies by tool type)
- **Handles**: Both `FunctionTool` (local Python) and `McpTool` (remote MCP server)

### Context Requirements

#### ToolContext
Minimal required context for tool execution:
```python
from google.adk.tools import ToolContext

# ToolContext requires InvocationContext as parent
tool_context = ToolContext(
    invocation_context=invocation_context,
    # Additional optional fields
)
```

#### InvocationContext
Parent context containing session/invocation metadata:
```python
from google.adk.invocation import InvocationContext

invocation_context = InvocationContext(
    # Minimal fields for simulator use
)
```

## Streamlit Integration Patterns

### Async Execution in Sync Context

Streamlit runs in a synchronous context. ADK tools are async. Solutions:

**Option 1: asyncio.run() (Recommended)**
```python
import asyncio

def execute_tool(tool, args, context):
    return asyncio.run(tool.run_async(args, context))
```

**Option 2: nest_asyncio (If event loop conflicts)**
```python
import asyncio
import nest_asyncio

nest_asyncio.apply()

def execute_tool(tool, args, context):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(tool.run_async(args, context))
```

### Session State Management

```python
import streamlit as st

# Initialize session state
if "session" not in st.session_state:
    st.session_state.session = SessionState(...)

# Update state
st.session_state.session.history.append(new_step)

# Access state
current_query = st.session_state.session.user_query
```

### Dynamic Form Generation

```python
def render_parameter(name: str, schema: Schema) -> Any:
    """Render appropriate widget for schema type."""
    
    if schema.enum:
        return st.selectbox(name, options=schema.enum)
    
    match schema.type:
        case Type.STRING:
            return st.text_input(name, help=schema.description)
        case Type.INTEGER:
            return st.number_input(name, step=1, help=schema.description)
        case Type.NUMBER:
            return st.number_input(name, help=schema.description)
        case Type.BOOLEAN:
            return st.checkbox(name, help=schema.description)
        case Type.OBJECT | Type.ARRAY:
            json_str = st.text_area(name, help=f"JSON: {schema.description}")
            return json.loads(json_str) if json_str else None
```

## Library Compatibility

### Tested Versions
- `google-adk`: >= 0.1.0 (pin specific version in production)
- `streamlit`: >= 1.30.0 (for stable session_state API)

### Known Limitations

1. **Private API Usage**: `_get_declaration()` is private; may need updates with ADK releases
2. **MCP Tool Latency**: Remote MCP tools have network overhead not present in FunctionTools
3. **Context Mocking**: Full ToolContext may require additional fields depending on tool implementation

## Alternative Approaches Considered

### Custom Python Reflection (Rejected)
- Could parse function signatures directly using `inspect` module
- **Why rejected**: ADK already provides this abstraction; custom parsing would diverge from what the model actually sees

### Direct Gemini API Calls (Rejected)
- Could call Gemini API to generate tool calls
- **Why rejected**: Defeats the purpose of human-in-the-loop; we want human to make decisions, not AI
