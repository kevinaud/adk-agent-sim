# Data Model: Simulator Run

**Date**: 2025-12-23  
**Plan**: [plan.md](plan.md)

## Entities

### SimulationSession

Represents a single simulation run from start to export.

```python
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.tools import BaseTool

class SessionState(Enum):
  """Session lifecycle states."""
  SELECTING_AGENT = "selecting_agent"  # Initial state, choosing agent
  AWAITING_QUERY = "awaiting_query"    # Agent selected, waiting for user query
  ACTIVE = "active"                     # In simulation loop
  COMPLETED = "completed"               # Final response submitted

class SimulationSession(BaseModel):
  """Tracks state for a single simulation run."""
  
  model_config = {"arbitrary_types_allowed": True}
  
  session_id: str = Field(description="Unique session identifier")
  agent_name: str = Field(description="Display name of selected agent")
  agent: Agent = Field(description="Reference to ADK Agent instance")
  tools: list[BaseTool] = Field(default_factory=list, description="Cached tools from agent")
  state: SessionState = Field(default=SessionState.SELECTING_AGENT)
  history: list["HistoryEntry"] = Field(default_factory=list)
  start_timestamp: float = Field(description="Session start time (epoch)")
  
  # For ADK context construction
  adk_session: Any = Field(default=None, description="ADK Session for ToolContext")
```

### HistoryEntry (Discriminated Union)

A single event in the session timeline.

```python
from datetime import datetime
from typing import Literal, Union
from pydantic import BaseModel, Field

class UserQuery(BaseModel):
  """Initial user query to start the session."""
  type: Literal["user_query"] = "user_query"
  content: str = Field(description="User's input text or structured data as JSON")
  timestamp: datetime = Field(default_factory=datetime.now)

class ToolCall(BaseModel):
  """Records a tool invocation request."""
  type: Literal["tool_call"] = "tool_call"
  tool_name: str
  arguments: dict[str, Any]
  call_id: str = Field(description="Unique ID for correlating with response")
  timestamp: datetime = Field(default_factory=datetime.now)

class ToolOutput(BaseModel):
  """Records a successful tool execution result."""
  type: Literal["tool_output"] = "tool_output"
  call_id: str = Field(description="Correlates with ToolCall.call_id")
  result: Any = Field(description="Tool return value")
  duration_ms: float = Field(description="Execution time in milliseconds")
  timestamp: datetime = Field(default_factory=datetime.now)

class ToolError(BaseModel):
  """Records a failed tool execution."""
  type: Literal["tool_error"] = "tool_error"
  call_id: str = Field(description="Correlates with ToolCall.call_id")
  error_type: str = Field(description="Exception class name")
  error_message: str = Field(description="Exception message")
  traceback: str | None = Field(default=None, description="Full traceback if available")
  duration_ms: float = Field(description="Time until failure in milliseconds")
  timestamp: datetime = Field(default_factory=datetime.now)

class FinalResponse(BaseModel):
  """Records the human's final answer."""
  type: Literal["final_response"] = "final_response"
  content: str = Field(description="Final response text or structured data as JSON")
  timestamp: datetime = Field(default_factory=datetime.now)

# Discriminated union for type-safe history handling
HistoryEntry = Union[UserQuery, ToolCall, ToolOutput, ToolError, FinalResponse]
```

### GoldenTraceBuilder

Assembles ADK `EvalCase` from session data.

```python
import time
import re
from google.adk.evaluation.eval_case import EvalCase, Invocation, IntermediateData
from google.genai.types import Content, Part, FunctionCall, FunctionResponse

class GoldenTraceBuilder:
  """Builds EvalCase from SimulationSession."""
  
  def __init__(self, session: SimulationSession):
    self.session = session
  
  def build(self) -> EvalCase:
    """Assemble complete EvalCase from session history."""
    # Extract components from history
    user_query = self._extract_user_query()
    final_response = self._extract_final_response()
    tool_uses, tool_responses = self._extract_tool_data()
    
    invocation = Invocation(
      invocation_id=f"{self.session.session_id}_inv_0",
      user_content=Content(parts=[Part(text=user_query)]),
      final_response=Content(parts=[Part(text=final_response)]) if final_response else None,
      intermediate_data=IntermediateData(
        tool_uses=tool_uses,
        tool_responses=tool_responses,
      ),
      creation_timestamp=self.session.start_timestamp,
    )
    
    return EvalCase(
      eval_id=self._generate_eval_id(),
      conversation=[invocation],
      creation_timestamp=self.session.start_timestamp,
    )
  
  def _generate_eval_id(self) -> str:
    """Generate eval_id as {snake_case_agent_name}_{iso_timestamp}."""
    snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', self.session.agent_name).lower()
    snake_name = re.sub(r'[^a-z0-9_]', '_', snake_name)
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self.session.start_timestamp))
    return f"{snake_name}_{iso_time}"
  
  def _extract_user_query(self) -> str:
    """Find UserQuery in history."""
    for entry in self.session.history:
      if isinstance(entry, UserQuery):
        return entry.content
    return ""
  
  def _extract_final_response(self) -> str | None:
    """Find FinalResponse in history."""
    for entry in self.session.history:
      if isinstance(entry, FinalResponse):
        return entry.content
    return None
  
  def _extract_tool_data(self) -> tuple[list[FunctionCall], list[FunctionResponse]]:
    """Extract tool calls and responses in chronological order."""
    tool_uses: list[FunctionCall] = []
    tool_responses: list[FunctionResponse] = []
    
    for entry in self.session.history:
      if isinstance(entry, ToolCall):
        tool_uses.append(FunctionCall(
          id=entry.call_id,
          name=entry.tool_name,
          args=entry.arguments,
        ))
      elif isinstance(entry, ToolOutput):
        tool_responses.append(FunctionResponse(
          id=entry.call_id,
          name=self._find_tool_name(entry.call_id),
          response={"result": entry.result},
        ))
      elif isinstance(entry, ToolError):
        tool_responses.append(FunctionResponse(
          id=entry.call_id,
          name=self._find_tool_name(entry.call_id),
          response={"error": {"type": entry.error_type, "message": entry.error_message}},
        ))
    
    return tool_uses, tool_responses
  
  def _find_tool_name(self, call_id: str) -> str:
    """Look up tool name from ToolCall by call_id."""
    for entry in self.session.history:
      if isinstance(entry, ToolCall) and entry.call_id == call_id:
        return entry.tool_name
    return "unknown"
```

## Relationships

```
SimulationSession
├── agent: Agent (1:1)
├── tools: list[BaseTool] (1:N, cached)
├── history: list[HistoryEntry] (1:N, ordered)
│   ├── UserQuery (1 per session)
│   ├── ToolCall (0..N)
│   ├── ToolOutput (0..N, paired with ToolCall)
│   ├── ToolError (0..N, paired with ToolCall)
│   └── FinalResponse (0..1, ends session)
└── adk_session: Session (1:1, for context)

GoldenTraceBuilder
└── builds → EvalCase
    └── conversation: list[Invocation]
        ├── user_content: Content
        ├── final_response: Content
        └── intermediate_data: IntermediateData
            ├── tool_uses: list[FunctionCall]
            └── tool_responses: list[FunctionResponse]
```

## State Transitions

```
SELECTING_AGENT ──[agent selected]──> AWAITING_QUERY
                                           │
                       [query submitted]───┘
                                           ▼
                                        ACTIVE ◄───────┐
                                           │           │
                          [tool executed]──┼───────────┘
                                           │
                     [final response]──────┘
                                           ▼
                                      COMPLETED
```

## Validation Rules

| Entity | Field | Constraint |
|--------|-------|------------|
| SimulationSession | agent_name | Non-empty string |
| SimulationSession | history | Must start with `UserQuery` when state >= ACTIVE |
| SimulationSession | history | Must end with `FinalResponse` when state == COMPLETED |
| ToolCall | call_id | Unique within session |
| ToolOutput/ToolError | call_id | Must match existing `ToolCall.call_id` |
| GoldenTraceBuilder | build() | Only valid when session.state == COMPLETED |
