# Data Model: Core Agent Simulator

**Feature**: 001-core-agent-simulator  
**Date**: 2025-12-22

## Core Entities

### SessionState

Represents the current state of a human-in-the-loop debugging session.

```python
@dataclass
class SessionState:
    """Active session state for the simulator."""
    
    agent_name: str
    """Name of the currently selected agent."""
    
    user_query: str | None = None
    """The initial user query/problem to solve."""
    
    history: list[TraceStep] = field(default_factory=list)
    """Chronological list of actions taken during the session."""
    
    started_at: datetime = field(default_factory=datetime.utcnow)
    """Timestamp when session began."""
    
    completed: bool = False
    """Whether the session has been finalized with a response."""
```

### TraceStep

Individual step in the execution trace.

```python
@dataclass
class TraceStep:
    """Single step in the session trace."""
    
    step_index: int
    """Zero-based index of this step in the trace."""
    
    type: Literal["tool_call", "final_answer"]
    """Type of step: tool execution or final response."""
    
    # Tool call fields (populated when type="tool_call")
    tool_name: str | None = None
    """Name of the tool that was called."""
    
    arguments: dict[str, Any] | None = None
    """Arguments passed to the tool."""
    
    output: Any = None
    """Return value from the tool execution."""
    
    error: str | None = None
    """Error message if tool execution failed."""
    
    # Final answer fields (populated when type="final_answer")
    content: str | None = None
    """The final text response to the user."""
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    """When this step was executed."""
```

### GoldenTrace

Export format for completed sessions.

```python
@dataclass
class GoldenTraceMetadata:
    """Metadata for the golden trace export."""
    
    agent_name: str
    """Name of the agent that was simulated."""
    
    timestamp: str
    """ISO 8601 timestamp of export."""
    
    user_query: str
    """The initial problem/query being solved."""


@dataclass
class GoldenTraceStep:
    """Simplified step format for export (matches ADK evaluation format)."""
    
    step_index: int
    type: Literal["tool_call", "final_answer"]
    
    # For tool_call
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    output: Any = None
    
    # For final_answer
    content: str | None = None


@dataclass
class GoldenTrace:
    """Complete golden trace export structure."""
    
    metadata: GoldenTraceMetadata
    trace: list[GoldenTraceStep]
```

## Relationships

```
┌─────────────────┐
│ AgentSimulator  │
│                 │
│ agents: dict    │──────┐
└────────┬────────┘      │
         │               │
         │ manages       │ contains
         ▼               ▼
┌─────────────────┐   ┌─────────────────┐
│  SessionState   │   │     Agent       │
│                 │   │   (from ADK)    │
│ agent_name      │   │                 │
│ user_query      │   │ canonical_tools │
│ history[]       │   │ canonical_instr │
│ started_at      │   └─────────────────┘
│ completed       │
└────────┬────────┘
         │
         │ contains
         ▼
┌─────────────────┐
│   TraceStep     │
│                 │
│ step_index      │
│ type            │
│ tool_name       │
│ arguments       │
│ output          │
│ content         │
└────────┬────────┘
         │
         │ exports to
         ▼
┌─────────────────┐
│  GoldenTrace    │
│                 │
│ metadata        │
│ trace[]         │
└─────────────────┘
```

## JSON Schema (Export Format)

See `contracts/golden-trace-schema.json` for the formal JSON Schema definition.

## State Transitions

```
Session Lifecycle:
                                    
  ┌─────────┐                       
  │  INIT   │  Select agent         
  └────┬────┘                       
       │                            
       ▼                            
  ┌─────────┐                       
  │  READY  │  Enter user query     
  └────┬────┘                       
       │                            
       ▼                            
  ┌─────────┐                       
  │ ACTIVE  │◄─────────┐            
  └────┬────┘          │            
       │               │            
       ├───Execute─────┘            
       │   Tool                     
       │                            
       ▼                            
  ┌─────────┐                       
  │COMPLETE │  Submit final response
  └────┬────┘                       
       │                            
       ▼                            
  ┌─────────┐                       
  │ EXPORT  │  Download trace       
  └─────────┘                       
```
