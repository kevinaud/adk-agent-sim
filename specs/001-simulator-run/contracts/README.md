# Internal Contracts: Simulator Run

**Date**: 2025-12-23  
**Plan**: [../plan.md](../plan.md)

This directory contains Python protocol/interface definitions for internal module contracts.

## Protocols

### SchemaFormRenderer

Responsible for converting `google.genai.types.Schema` to NiceGUI form elements.

```python
# contracts/schema_form.py
from typing import Any, Protocol
from google.genai.types import Schema

class SchemaFormRenderer(Protocol):
  """Protocol for Schema → UI form conversion."""
  
  def render(
    self,
    schema: Schema,
    *,
    on_change: Callable[[dict[str, Any]], None] | None = None,
  ) -> dict[str, Any]:
    """
    Render a schema as a form and return collected values.
    
    Args:
      schema: The google.genai.types.Schema to render
      on_change: Optional callback when any field value changes
    
    Returns:
      Dictionary of field_name → current_value
    
    Raises:
      ValueError: If schema type is unsupported
    """
    ...
  
  def validate(self, schema: Schema, values: dict[str, Any]) -> list[str]:
    """
    Validate collected values against schema constraints.
    
    Returns:
      List of validation error messages (empty if valid)
    """
    ...
```

### ToolExecutor

Responsible for async tool execution with cancellation support.

```python
# contracts/tool_executor.py
from typing import Any, Protocol
from google.adk.tools import BaseTool

class ExecutionResult:
  """Result of tool execution."""
  success: bool
  result: Any | None  # Tool return value if success
  error: Exception | None  # Exception if failure
  duration_ms: float
  cancelled: bool

class ToolExecutor(Protocol):
  """Protocol for async tool execution."""
  
  @property
  def is_running(self) -> bool:
    """Whether a tool is currently executing."""
    ...
  
  @property
  def elapsed_ms(self) -> float:
    """Milliseconds since execution started (0 if not running)."""
    ...
  
  async def execute(
    self,
    tool: BaseTool,
    arguments: dict[str, Any],
    session: "SimulationSession",
  ) -> ExecutionResult:
    """
    Execute a tool with the given arguments.
    
    Args:
      tool: The ADK tool to execute
      arguments: Arguments matching the tool's schema
      session: Current simulation session (for context construction)
    
    Returns:
      ExecutionResult with success/failure details
    """
    ...
  
  def cancel(self) -> None:
    """Request cancellation of the running tool (if any)."""
    ...
```

### TraceExporter

Responsible for converting session data to ADK EvalCase.

```python
# contracts/trace_exporter.py
from typing import Protocol
from google.adk.evaluation.eval_case import EvalCase

class TraceExporter(Protocol):
  """Protocol for session → EvalCase conversion."""
  
  def export(self, session: "SimulationSession") -> EvalCase:
    """
    Build an EvalCase from a completed session.
    
    Args:
      session: Completed simulation session
    
    Returns:
      EvalCase conforming to ADK evaluation schema
    
    Raises:
      ValueError: If session is not in COMPLETED state
    """
    ...
  
  def export_json(self, session: "SimulationSession", indent: int = 2) -> str:
    """
    Export session as JSON string.
    
    Args:
      session: Completed simulation session
      indent: JSON indentation level
    
    Returns:
      JSON string representation of EvalCase
    """
    ...
```

### SimulationController

Orchestrates the simulation flow between UI and business logic.

```python
# contracts/controller.py
from typing import Any, Callable, Protocol
from google.adk.agents import Agent

class SimulationController(Protocol):
  """Protocol for simulation orchestration."""
  
  @property
  def available_agents(self) -> dict[str, Agent]:
    """Dictionary of agent_name → Agent instance."""
    ...
  
  @property
  def current_session(self) -> "SimulationSession | None":
    """Active session or None if not started."""
    ...
  
  async def select_agent(self, agent_name: str) -> None:
    """
    Select an agent and initialize tools.
    
    Args:
      agent_name: Key from available_agents dict
    
    Raises:
      KeyError: If agent_name not found
    """
    ...
  
  async def start_session(self, user_query: str | dict[str, Any]) -> None:
    """
    Start a new session with the given user query.
    
    Args:
      user_query: Plain text or structured input (if input_schema defined)
    """
    ...
  
  async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> None:
    """
    Execute a tool and record results in session history.
    
    Args:
      tool_name: Name of the tool to execute
      arguments: Arguments for the tool
    """
    ...
  
  def cancel_tool(self) -> None:
    """Cancel the currently executing tool (if any)."""
    ...
  
  async def submit_final_response(self, response: str | dict[str, Any]) -> None:
    """
    Submit final response and transition to COMPLETED state.
    
    Args:
      response: Plain text or structured output (if output_schema defined)
    """
    ...
  
  def export_trace(self) -> str:
    """
    Export current session as Golden Trace JSON.
    
    Returns:
      JSON string of EvalCase
    
    Raises:
      ValueError: If session not completed
    """
    ...
```

## UI Component Contracts

### HistoryPanelProps

```python
# contracts/ui.py
from typing import TypedDict

class HistoryPanelProps(TypedDict):
  """Props for the history panel component."""
  entries: list["HistoryEntry"]
  on_entry_click: Callable[["HistoryEntry"], None] | None

class ActionPanelProps(TypedDict):
  """Props for the action panel component."""
  tools: list["BaseTool"]
  has_output_schema: bool
  on_tool_select: Callable[[str], None]
  on_final_response: Callable[[], None]

class ToolExecutorProps(TypedDict):
  """Props for the tool executor component."""
  tool: "BaseTool"
  on_execute: Callable[[dict[str, Any]], None]
  on_cancel: Callable[[], None]
  is_running: bool
  elapsed_ms: float
```

## File Organization

```text
contracts/
├── README.md           # This file
├── schema_form.py      # SchemaFormRenderer protocol
├── tool_executor.py    # ToolExecutor protocol + ExecutionResult
├── trace_exporter.py   # TraceExporter protocol
├── controller.py       # SimulationController protocol
└── ui.py               # UI component prop types
```

Note: These protocols are for documentation and type checking. They are NOT enforced at runtime but guide implementation.
