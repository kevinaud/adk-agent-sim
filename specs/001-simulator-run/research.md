# Research: Simulator Run

**Date**: 2025-12-23  
**Plan**: [plan.md](plan.md)

## Research Task 1: NiceGUI Async Patterns

**Question**: How to run `async` tool execution from NiceGUI event handlers without blocking UI?

**Findings**:

NiceGUI is built on FastAPI/Starlette and runs natively on `asyncio`. Event handlers can be `async def` functions directly.

```python
from nicegui import ui

async def on_execute_tool():
  # This runs on the asyncio event loop - no blocking
  result = await tool.run_async(args, context)
  ui.notify(f"Result: {result}")

ui.button("Execute", on_click=on_execute_tool)
```

For long-running operations with cancellation:

```python
import asyncio

class ToolExecutor:
  def __init__(self):
    self.cancel_event = asyncio.Event()
    self.current_task: asyncio.Task | None = None
  
  async def execute(self, tool, args, context):
    self.cancel_event.clear()
    self.current_task = asyncio.current_task()
    try:
      # Run with ability to check cancellation
      result = await tool.run_async(args, context)
      return result
    except asyncio.CancelledError:
      return None
  
  def cancel(self):
    if self.current_task:
      self.current_task.cancel()
```

**Decision**: Use `async def` handlers with `asyncio.Task.cancel()` for abort functionality.

---

## Research Task 2: ADK ToolContext Construction

**Question**: What fields are required to construct a valid `ToolContext` and `InvocationContext`?

**Findings**:

From ADK source inspection (`google.adk.tools.tool_context` and `google.adk.agents.invocation_context`):

### InvocationContext (Required for tool execution)

```python
from google.adk.agents.invocation_context import InvocationContext

class InvocationContext(BaseModel):
  invocation_id: str = ""
  agent: Agent  # The agent being simulated
  session: Session  # ADK Session object
  # ... other fields with defaults
```

### ToolContext (Passed to tools)

```python
from google.adk.tools.tool_context import ToolContext

# ToolContext is typically created by the framework
# For simulation, we need minimal fields:
tool_context = ToolContext(
  invocation_context=invocation_context,
  function_call_id=str(uuid.uuid4()),
  # ... other fields have defaults
)
```

**Key Discovery**: We need to create a minimal ADK `Session` object to satisfy the `InvocationContext`. This can be an in-memory session with no persistence.

```python
from google.adk.sessions import InMemorySessionService, Session

session_service = InMemorySessionService()
session = await session_service.create_session(
  app_name="simulator",
  user_id="wizard"
)
```

**Decision**: Use `InMemorySessionService` to create ADK Sessions. Wrap context creation in `execution/context_factory.py`.

---

## Research Task 3: Schema.items Handling

**Question**: How does `google.genai.types.Schema` represent array item schemas?

**Findings**:

From `google.genai.types.Schema`:

```python
class Schema(_common.BaseModel):
  type: Optional[Type] = None
  items: Optional[Schema] = None  # Schema for array items
  properties: Optional[dict[str, Schema]] = None  # For OBJECT
  required: Optional[list[str]] = None
  enum: Optional[list[str]] = None
  description: Optional[str] = None
  # ... other fields
```

For arrays:
- `schema.type == Type.ARRAY`
- `schema.items` contains the `Schema` for each array element
- If `schema.items` is `None`, treat as `list[Any]` (JSON textarea fallback)

Example:
```python
# Array of strings
Schema(type=Type.ARRAY, items=Schema(type=Type.STRING))

# Array of objects
Schema(
  type=Type.ARRAY,
  items=Schema(
    type=Type.OBJECT,
    properties={"name": Schema(type=Type.STRING)},
    required=["name"]
  )
)
```

**Decision**: Recursive rendering handles arrays by rendering `schema.items` for each list item. Dynamic add/remove buttons manage list length.

---

## Research Task 4: EvalCase Structure Verification

**Question**: Confirm field names and types match ADK evaluation expectations.

**Findings**:

From `google.adk.evaluation.eval_case`:

```python
class EvalCase(EvalBaseModel):
  eval_id: str
  conversation: Optional[StaticConversation] = None  # list[Invocation]
  session_input: Optional[SessionInput] = None
  creation_timestamp: float = 0.0
  # ... other optional fields

class Invocation(EvalBaseModel):
  invocation_id: str = ""
  user_content: genai_types.Content
  final_response: Optional[genai_types.Content] = None
  intermediate_data: Optional[IntermediateDataType] = None
  creation_timestamp: float = 0.0

class IntermediateData(EvalBaseModel):
  tool_uses: list[genai_types.FunctionCall] = []
  tool_responses: list[genai_types.FunctionResponse] = []
```

**Key Points**:
- `eval_id` is a string (our format: `{agent_name}_{timestamp}`)
- `conversation` is `list[Invocation]` (we create one per session)
- `user_content` is `genai_types.Content` (wraps text in `Part`)
- `tool_uses` expects `genai_types.FunctionCall` (has `name`, `args`, `id`)
- `tool_responses` expects `genai_types.FunctionResponse` (has `name`, `response`, `id`)

**Decision**: Build `EvalCase` directly using ADK's Pydantic models. Export via `model_dump_json(indent=2)`.

---

## Summary

| Research Task | Decision | Confidence |
|---------------|----------|------------|
| NiceGUI async | Use native `async def` handlers + `Task.cancel()` | High |
| ToolContext | Use `InMemorySessionService` for ADK Session creation | High |
| Schema.items | Recursive rendering with dynamic list UI | High |
| EvalCase | Direct use of ADK Pydantic models | High |

All research questions resolved. Ready for Phase 1 design.
