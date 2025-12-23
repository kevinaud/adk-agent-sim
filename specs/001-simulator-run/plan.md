# Implementation Plan: Simulator Run

**Branch**: `001-simulator-run` | **Date**: 2025-12-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-simulator-run/spec.md`

## Summary

Implement the core "Simulator Run" feature enabling human-in-the-loop simulation of ADK agents via a NiceGUI-based web interface. The user selects an agent, enters a query, manually invokes tools through dynamically-generated forms, and exports the session as an ADK-compatible `EvalCase` Golden Trace.

**Technical Approach**: In-process library pattern using NiceGUI (FastAPI/Starlette-based) running on the Python event loop with direct access to Agent instances—no IPC or pickling required.

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: `nicegui` (UI), `google-adk` (Agent framework), `pydantic` (data models)  
**Storage**: N/A (ephemeral in-memory sessions only)  
**Testing**: `pytest` with `pytest-asyncio` for async tool execution tests  
**Target Platform**: Any platform with a modern browser (NiceGUI serves localhost)  
**Project Type**: Single project (Python library)  
**Performance Goals**: UI response <200ms, tool execution bounded only by underlying tool  
**Constraints**: No persistence, single-agent-per-session, sequential tool execution  
**Scale/Scope**: Single developer usage, 1 session at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Library-First | ✅ PASS | `AgentSimulator` class importable via `from adk_agent_sim import AgentSimulator` |
| II. Wrapper Integration | ✅ PASS | Accepts `dict[str, Agent]` in constructor, no proprietary formats |
| III. Wizard of Oz | ✅ PASS | Human selects tools, fills forms, decides final response manually |
| IV. ADK Dependency | ✅ PASS | Uses `canonical_tools()`, `_get_declaration()`, `run_async()` |
| V. Golden Trace | ✅ PASS | Exports `EvalCase` via `model_dump_json()` |
| VI. Hermetic Environment | ✅ PASS | `nicegui` added to `pyproject.toml`, no manual setup |
| VII. Strict Standards | ✅ PASS | All code must pass `ruff` (2-space) and `pyright` strict |
| VIII. Flexible UI | ✅ PASS | NiceGUI chosen during planning phase as per Constitution |

**No violations requiring justification.**

## Project Structure

### Documentation (this feature)

```text
specs/001-simulator-run/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal Python interfaces)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
adk_agent_sim/
├── __init__.py                    # Public API: AgentSimulator
├── simulator.py                   # AgentSimulator class (entry point)
├── controller.py                  # SimulationController orchestration
├── session.py                     # SimulationSession state machine
├── models/
│   ├── __init__.py
│   ├── history.py                 # HistoryEntry discriminated union types
│   └── trace.py                   # GoldenTrace builder wrapping EvalCase
├── ui/
│   ├── __init__.py
│   ├── app.py                     # NiceGUI app setup and routing
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── agent_select.py        # Agent selection screen (FR-007)
│   │   └── simulation.py          # Main simulation page
│   ├── components/
│   │   ├── __init__.py
│   │   ├── schema_form.py         # Universal Schema → Form renderer (FR-004)
│   │   ├── history_panel.py       # Chat history display (FR-015-017)
│   │   ├── action_panel.py        # Tool/Response action selector
│   │   ├── tool_executor.py       # Tool form + execution UI (FR-030-031)
│   │   └── system_prompt.py       # Collapsible system instructions (FR-008)
│   └── styles.py                  # Shared CSS/styling constants
├── execution/
│   ├── __init__.py
│   ├── context_factory.py         # ToolContext/InvocationContext builders (FR-032-033)
│   └── tool_runner.py             # Async tool execution wrapper (FR-011)
└── export/
    ├── __init__.py
    └── golden_trace.py            # EvalCase assembly + JSON export (FR-018-025)

tests/
├── conftest.py                    # Shared fixtures (mock agents, tools)
├── unit/
│   ├── test_schema_form.py        # Schema → Form rendering tests
│   ├── test_session.py            # SimulationSession state tests
│   ├── test_history.py            # HistoryEntry model tests
│   └── test_golden_trace.py       # EvalCase export validation
└── integration/
    ├── test_tool_execution.py     # Real tool execution via ADK
    └── test_simulation_flow.py    # End-to-end session workflow
```

**Structure Decision**: Single project layout extending existing `adk_agent_sim/` package. UI components organized under `ui/` with separation between pages (full screens) and components (reusable widgets). Business logic split between `session.py` (state), `execution/` (ADK integration), and `export/` (Golden Trace generation).

## Functional Requirements Mapping

### FR → Implementation Mapping

| FR | Component | Implementation |
|----|-----------|----------------|
| FR-001 | `controller.py` | `await agent.canonical_tools()` on agent selection |
| FR-002 | `controller.py` | `tool._get_declaration()` cached per tool |
| FR-003 | `ui/components/schema_form.py` | `render_schema_form(declaration.parameters)` |
| FR-004 | `ui/components/schema_form.py` | Recursive `_render_field(schema, path)` with type dispatch |
| FR-005 | `ui/components/schema_form.py` | `ui.label(schema.description)` for each field |
| FR-006 | `ui/components/schema_form.py` | Pre-submit validation checking `schema.required` |
| FR-007 | `ui/pages/agent_select.py` | `ui.select` with agent names, locks on selection |
| FR-008 | `ui/components/system_prompt.py` | `ui.expansion` with `agent.canonical_instruction()` |
| FR-009 | `ui/pages/simulation.py` | Text input or schema form for initial query |
| FR-010 | `ui/pages/simulation.py` | Schema form rendered if `agent.input_schema` exists |
| FR-011 | `ui/components/history_panel.py` | Display conversation history |
| FR-012 | `ui/components/action_panel.py` | Two action choices: "Call a Tool" or "Send Final Response" |
| FR-013 | `execution/tool_runner.py` | `await tool.run_async(args, tool_context)` |
| FR-014 | `session.py` | `session.add_tool_output(result)` → UI refresh |
| FR-015 | `ui/components/action_panel.py` | Schema form for `agent.output_schema` |
| FR-016 | `ui/components/action_panel.py` | Pydantic validation before submit |
| FR-017 | `session.py` | `list[HistoryEntry]` in `SimulationSession` |
| FR-018 | `ui/components/history_panel.py` | Render each `HistoryEntry` variant |
| FR-019 | `ui/components/history_panel.py` | Distinct card styles per entry type |
| FR-020 | `export/golden_trace.py` | `GoldenTraceBuilder.build() → EvalCase` |
| FR-021 | `export/golden_trace.py` | Uses `google.adk.evaluation.eval_case.EvalCase` directly |
| FR-022 | `export/golden_trace.py` | `f"{snake_case(agent.name)}_{iso_timestamp()}"` |
| FR-023 | `export/golden_trace.py` | Single `Invocation` per session |
| FR-024 | `export/golden_trace.py` | `Content(parts=[Part(text=query)])` |
| FR-025 | `export/golden_trace.py` | `Content(parts=[Part(text=response)])` |
| FR-026 | `export/golden_trace.py` | `IntermediateData(tool_uses=[...], tool_responses=[...])` |
| FR-027 | `export/golden_trace.py` | `time.time()` at session start |
| FR-028 | `execution/tool_runner.py` | `try/except` around `run_async()` |
| FR-029 | `session.py` | `ToolError` history entry with exc info |
| FR-030 | `ui/pages/simulation.py` | Session state remains `active` after error |
| FR-031 | `export/golden_trace.py` | `FunctionResponse(response={"error": ...})` |
| FR-032 | `ui/components/tool_executor.py` | `ui.label` with reactive timer (`asyncio` based) |
| FR-033 | `ui/components/tool_executor.py` | `ui.button("Cancel")` sets `asyncio.Event` |
| FR-034 | `execution/context_factory.py` | `create_tool_context(session, tool)` |
| FR-035 | `execution/context_factory.py` | `create_invocation_context(session)` |

## Complexity Tracking

> No Constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | — | — |

---

## Phase 0: Research

### Research Tasks

1. **NiceGUI async patterns**: How to run `async` tool execution from NiceGUI event handlers without blocking UI.
2. **ADK ToolContext construction**: What fields are required to construct a valid `ToolContext` and `InvocationContext`.
3. **Schema.items handling**: How `google.genai.types.Schema` represents array item schemas.
4. **EvalCase structure verification**: Confirm field names and types match ADK evaluation expectations.

### Decisions

| Topic | Decision | Rationale | Alternatives Rejected |
|-------|----------|-----------|----------------------|
| UI Framework | NiceGUI | Native Python, runs on asyncio event loop, FastAPI-based (direct Agent access) | Streamlit (sync model), Gradio (limited customization), React (requires separate backend) |
| State Management | Python class instances | Simple, type-safe, no serialization overhead | Redux-like (overkill), database (persistence not needed) |
| Form Rendering | Recursive `render_schema_form()` | Handles nested OBJECT/ARRAY via recursion | Flat form (doesn't support nesting), JSON textarea (poor UX) |
| Tool Cancellation | `asyncio.Event` + `asyncio.wait_for` | Standard async pattern, no external deps | Threading (GIL issues), subprocess (IPC overhead) |

---

## Phase 1: Design

### Data Model

See [data-model.md](data-model.md) for full entity definitions.

**Key Entities:**
- `SimulationSession`: Holds agent ref, history list, state enum
- `HistoryEntry`: Discriminated union (`UserQuery | ToolCall | ToolOutput | ToolError | FinalResponse`)
- `GoldenTraceBuilder`: Assembles `EvalCase` from session data

### Contracts

See [contracts/README.md](contracts/README.md) for internal Python interface definitions.

**Key Interfaces:**
- `SchemaFormRenderer`: Protocol for `Schema → UI` conversion
- `ToolExecutor`: Protocol for async tool invocation with cancellation
- `TraceExporter`: Protocol for session → `EvalCase` conversion
- `SimulationController`: Protocol for simulation orchestration

### Quickstart

See [quickstart.md](quickstart.md) for developer usage guide.

```python
from adk_agent_sim import AgentSimulator
from my_project.agents import my_agent

simulator = AgentSimulator(agents={"MyAgent": my_agent})
simulator.run()  # Opens browser at http://localhost:8080
```

---

## Dependencies

### New Dependencies (add to `pyproject.toml`)

```toml
[project.dependencies]
nicegui = ">=2.0.0"
```

### Dev Container Updates

None required—`nicegui` is a pure Python package installable via `uv`.

---

## Quality Gates Checklist

- [ ] All new files use 2-space indentation (`ruff format`)
- [ ] All new files pass `ruff check` with zero errors
- [ ] All new files pass `pyright --strict` with zero errors
- [ ] Unit tests cover Schema → Form mapping for all `Type` variants
- [ ] Integration test validates `EvalCase` export parses correctly
- [ ] Manual smoke test: complete simulation session with demo agent
