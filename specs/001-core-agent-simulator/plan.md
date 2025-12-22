# Implementation Plan: Core Agent Simulator

**Branch**: `001-core-agent-simulator` | **Date**: 2025-12-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-core-agent-simulator/spec.md`

## Summary

Build a "Wizard of Oz" human-in-the-loop debugging tool that allows developers to roleplay as their ADK agents. The system uses Google ADK's native abstractions (`canonical_tools()`, `_get_declaration()`, `run_async()`) for tool discovery and execution, with Streamlit providing the UI layer for dynamic form generation, session management, and Golden Trace export.

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: google-adk, streamlit  
**Storage**: In-memory session state (Streamlit st.session_state), JSON file export  
**Testing**: pytest, pytest-asyncio  
**Target Platform**: Local development (web browser via Streamlit)  
**Project Type**: Single Python library with Streamlit UI  
**Performance Goals**: Tool form rendering <500ms, tool execution overhead <1s  
**Constraints**: Must work within Streamlit's synchronous execution model while calling async ADK methods  
**Scale/Scope**: Single developer debugging session, 1-50 tools per agent

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Library-First Principle (Article I)
- [x] Core functionality exposed as importable `AgentSimulator` class
- [x] UI is separate concern from introspection/execution logic
- [x] Can be used programmatically before any CLI exposure

### ADK Native Integration (Article II)
- [x] Using `agent.canonical_tools()` for discovery
- [x] Using `tool._get_declaration()` for schema
- [x] Using `tool.run_async()` for execution
- [x] No custom Python reflection

### Streamlit UI Standards (Article III)
- [x] Dynamic form generation from JSON Schema
- [x] Consistent widget mapping defined
- [x] Session state for history tracking

### Test-First Development (Article IV)
- [x] Plan includes test structure
- [x] Mock strategies defined for ADK objects

### Golden Trace Compliance (Article V)
- [x] Schema defined in spec
- [x] Export format documented

## Project Structure

### Documentation (this feature)

```text
specs/001-core-agent-simulator/
├── plan.md              # This file
├── research.md          # ADK integration research
├── data-model.md        # Session and Trace models
├── quickstart.md        # Key validation scenarios
├── contracts/           # API contracts
│   └── golden-trace-schema.json
└── tasks.md             # Generated tasks
```

### Source Code (repository root)

```text
adk_agent_sim/
├── __init__.py          # Public exports: AgentSimulator
├── simulator.py         # Main AgentSimulator class
├── introspection.py     # ADK agent/tool introspection utilities
├── execution.py         # Tool execution with async bridging
├── schema_renderer.py   # JSON Schema → Streamlit widget mapping
├── session.py           # Session state and history management
├── trace_export.py      # Golden Trace JSON generation
├── ui/
│   ├── __init__.py
│   ├── main.py          # Streamlit app entry point
│   ├── sidebar.py       # Agent selection, tool list
│   ├── tool_form.py     # Dynamic tool parameter forms
│   ├── chat_history.py  # Conversation/trace display
│   └── export_panel.py  # Download and export controls
└── demo/                # Existing demo code

tests/
├── conftest.py          # Shared fixtures, mock ADK objects
├── unit/
│   ├── test_introspection.py
│   ├── test_schema_renderer.py
│   ├── test_session.py
│   └── test_trace_export.py
├── integration/
│   └── test_tool_execution.py
└── fixtures/
    └── mock_agents.py   # Mock Agent and Tool implementations
```

**Structure Decision**: Single project structure. The library is a cohesive unit with UI as an internal module. No separate frontend/backend split needed since Streamlit handles both.

## Complexity Tracking

No constitution violations. Design follows all principles.

## Phase 0: Research

### ADK Integration Points

1. **Tool Discovery**: `agent.canonical_tools()` returns `list[BaseTool]`
2. **Schema Extraction**: `tool._get_declaration()` returns `FunctionDeclaration` with:
   - `name`: string
   - `description`: string
   - `parameters`: JSON Schema object with `properties`, `required`
3. **Execution**: `tool.run_async(args, tool_context)` requires:
   - `ToolContext` object (needs investigation for minimal mock)
   - `InvocationContext` as parent context
4. **Agent Metadata**: `agent.canonical_instruction()` for system prompt

### Streamlit Async Bridging

```python
import asyncio

def _run_async(coro):
    """Run async coroutine in Streamlit's sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # Running in async context (rare in Streamlit)
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    else:
        # Standard case: no running loop
        return asyncio.run(coro)
```

### Widget Mapping Strategy

| JSON Schema Type | Streamlit Widget | Notes |
|-----------------|------------------|-------|
| `string` | `st.text_input` | Default for unknown |
| `string` + `enum` | `st.selectbox` | Dropdown with choices |
| `integer` | `st.number_input(step=1)` | Integer constraint |
| `number` | `st.number_input` | Float allowed |
| `boolean` | `st.checkbox` | True/False |
| `object` | `st.text_area` | JSON input, parsed |
| `array` | `st.text_area` | JSON array input |

## Phase 1: Design

### Core Classes

#### AgentSimulator
```python
class AgentSimulator:
    """Main entry point for the ADK Agent Simulator."""
    
    def __init__(self, agents: dict[str, Agent]):
        self.agents = agents
    
    def run(self, port: int = 8501) -> None:
        """Launch Streamlit UI."""
        # Launches streamlit run with appropriate config
```

#### Session
```python
@dataclass
class SessionState:
    agent_name: str
    user_query: str | None
    history: list[TraceStep]
    started_at: datetime
    
@dataclass
class TraceStep:
    step_index: int
    type: Literal["tool_call", "final_answer"]
    tool_name: str | None  # For tool_call
    arguments: dict | None  # For tool_call
    output: Any | None      # For tool_call
    content: str | None     # For final_answer
```

#### SchemaRenderer
```python
class SchemaRenderer:
    """Converts JSON Schema to Streamlit form widgets."""
    
    def render_form(self, declaration: FunctionDeclaration) -> dict:
        """Render form and return collected values."""
```

### File Creation Order

1. Create `contracts/golden-trace-schema.json` with JSON Schema
2. Create test files: `test_schema_renderer.py`, `test_session.py`, `test_trace_export.py`
3. Create source files to make tests pass:
   - `session.py` - Session/TraceStep dataclasses
   - `trace_export.py` - JSON serialization
   - `schema_renderer.py` - Widget mapping
   - `introspection.py` - ADK wrapper utilities
   - `execution.py` - Async bridging and execution
4. Create UI modules after core logic is tested
5. Create `simulator.py` to wire everything together

## Phase 2: Implementation Phases

### Phase 2.1: Core Data Models (MVP Foundation)
- [ ] Define SessionState and TraceStep dataclasses
- [ ] Implement GoldenTrace export with schema validation
- [ ] Unit tests for serialization

### Phase 2.2: ADK Integration Layer
- [ ] Implement introspection utilities (canonical_tools wrapper)
- [ ] Implement schema extraction (get_declaration wrapper)
- [ ] Implement async execution bridge
- [ ] Mock ADK objects for testing
- [ ] Integration tests with real ADK agents

### Phase 2.3: Schema Renderer
- [ ] Implement type-to-widget mapping
- [ ] Handle required field validation
- [ ] Handle enum/choices rendering
- [ ] Handle complex object JSON input
- [ ] Unit tests for all type mappings

### Phase 2.4: Streamlit UI
- [ ] Main app structure with session state
- [ ] Sidebar: agent selector, tool list
- [ ] Tool form: dynamic rendering
- [ ] Chat history: event log display
- [ ] Export panel: download button

### Phase 2.5: Integration & Polish
- [ ] Wire all components in AgentSimulator.run()
- [ ] End-to-end testing with demo agent
- [ ] Error handling and edge cases
- [ ] Documentation and examples

## Dependencies

```toml
# pyproject.toml additions
dependencies = [
    "google-adk",
    "streamlit>=1.30.0",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
]
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ADK `_get_declaration()` is private API | Document version pinning; create wrapper for isolation |
| ToolContext mocking complexity | Start with minimal mock; expand based on actual requirements |
| Streamlit session state race conditions | Use explicit state management; avoid concurrent modifications |
| Complex nested schemas | Fall back to JSON text area; document limitation |
