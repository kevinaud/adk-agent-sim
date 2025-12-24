# Data Model: E2E Test Suite

**Feature**: 002-e2e-test-suite  
**Date**: 2024-12-23 (Updated: 2025-12-23)  
**Purpose**: Define test data structures and test agent configuration  
**Status**: ✅ Aligned with research.md decisions

## Overview

The E2E test suite doesn't introduce new domain entities to the main application. Instead, it defines:
1. Test fixtures for server lifecycle
2. A dedicated test agent with predictable tool schemas
3. Test data constants for reproducible scenarios

---

## Test Agent Definition

The E2E tests require an agent with tools exhibiting specific schema types. This agent is defined in `tests/fixtures/agents/test_agent/` (per clarification decisions).

### Test Agent: `TestAgent`

**Location**: `tests/fixtures/agents/test_agent/agent.py`

```
Agent
├── name: "TestAgent"
├── description: "Agent with diverse tools for E2E testing"
├── model: "gemini-2.5-flash"
└── tools: [FunctionTool only, no MCP]
    ├── add_numbers(a: int, b: int) -> int
    ├── greet(name: str, formal: bool) -> str
    ├── get_status(level: Literal["low", "medium", "high"]) -> str
    └── fail_always() -> str  [raises RuntimeError]
```

### Tool Schemas

| Tool | Parameters | Return | Purpose | Test Case |
|------|------------|--------|---------|-----------|
| `add_numbers` | `a: int`, `b: int` | `int` | Happy path with number inputs | TC-01 |
| `greet` | `name: str`, `formal: bool` | `str` | String input + checkbox widget | TC-02 |
| `get_status` | `level: Literal["low", "medium", "high"]` | `str` | Dropdown/enum widget | TC-02 |
| `fail_always` | None | `str` | Error handling verification | TC-03 |

---

## Test Fixture Structure

### Session-Scoped Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `run_server` | session | Starts NiceGUI server on port 8081, yields base URL |
| `browser` | session | Playwright browser instance (headless Chromium) |

### Function-Scoped Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `page` | function | Fresh browser page/tab for each test |
| `base_url` | function | URL of running server (from `run_server`) |

### Fixture Dependencies

```
run_server (session)
    └── base_url (function)
            └── page (function)
                    └── test functions
```

---

## Test Data Constants

### URLs

| Constant | Value | Description |
|----------|-------|-------------|
| `TEST_SERVER_PORT` | `8081` | Dedicated port for E2E tests |
| `TEST_BASE_URL` | `http://127.0.0.1:8081` | Full base URL |

### Timeouts

| Constant | Value | Description |
|----------|-------|-------------|
| `SERVER_STARTUP_TIMEOUT` | `10s` | Max wait for server ready |
| `ELEMENT_TIMEOUT` | `10s` | Max wait for UI elements |
| `TOOL_EXECUTION_TIMEOUT` | `30s` | Max wait for tool to complete |

### Test Inputs

| Constant | Value | Use Case |
|----------|-------|----------|
| `HAPPY_PATH_QUERY` | `"Calculate 5 + 3"` | TC-01 initial query |
| `ADD_INPUT_A` | `5` | TC-01 first operand |
| `ADD_INPUT_B` | `3` | TC-01 second operand |
| `EXPECTED_ADD_RESULT` | `8` | TC-01 assertion |
| `GREET_NAME` | `"Alice"` | TC-02 string input |
| `GREET_FORMAL` | `True` | TC-02 boolean input |
| `STATUS_ENUM_VALUE` | `"medium"` | TC-02 enum selection |
| `ERROR_TOOL_NAME` | `"fail_always"` | TC-03 error trigger |
| `JSON_DATA_RESULT` | `'{"nested": {"key": "value"}}'` | TC-05 JSON auto-parse |
| `TEST_EVAL_SET_PATH` | `"/tmp/test_evals.json"` | TC-01 EvalSet export path |

---

## Page Object Patterns (Optional)

If test complexity grows, these page objects can be introduced:

### AgentSelectPage

```
AgentSelectPage
├── agent_cards: List[Locator]    # Available agent cards
├── select_agent(name: str)       # Click agent card, wait for navigation
├── get_agent_names() -> List[str]
└── get_agent_description(name: str) -> str | None  # TC-07: verify description
```

### SimulationPage

```
SimulationPage
├── query_input: Locator          # Initial query textarea
├── start_button: Locator         # "Start Session" button
├── tool_catalog: Locator         # Tool catalog with all tools
├── tool_cards: List[Locator]     # Individual tool cards with metadata
├── tool_form: Locator            # Dynamic parameter form
├── execute_button: Locator       # "Execute" button
├── history_panel: Locator        # History entries container
├── event_blocks: List[Locator]   # Individual event blocks
├── expand_all_button: Locator    # "Expand All" per event
├── collapse_all_button: Locator  # "Collapse All" per event
├── final_response_input: Locator # Final response textarea
├── submit_button: Locator        # "Submit Final Response" button
├── export_button: Locator        # "Export" button (after completion)
│
├── enter_query(text: str)
├── select_tool(name: str)        # Click tool in catalog
├── get_tool_description(name: str) -> str  # TC-06: catalog metadata
├── fill_form(values: dict)
├── execute_tool()
├── get_history_entries() -> List[HistoryEntry]
├── is_section_expanded(event_index: int, section: str) -> bool  # TC-05
├── toggle_section(event_index: int, section: str)  # TC-05
├── click_expand_all(event_index: int)  # TC-05
├── click_collapse_all(event_index: int)  # TC-05
├── submit_final_response(text: str)
├── click_export()  # TC-01
└── wait_for_tool_result(timeout: int)
```

**Note**: Page objects are optional for the initial tests. They can be introduced in a later iteration if test maintenance becomes burdensome.

---

## State Transitions for TC-04

```
┌─────────────────┐
│  Fresh Session  │ ← Page load / Reload
└────────┬────────┘
         │ Enter query + Start
         ▼
┌─────────────────┐
│     Active      │ ← Tools available
└────────┬────────┘
         │ Execute tools...
         ▼
┌─────────────────┐
│  Has History    │ ← History entries visible
└────────┬────────┘
         │ Page reload (TC-04 trigger)
         ▼
┌─────────────────┐
│  Fresh Session  │ ← History cleared (verify)
└─────────────────┘
```

TC-04 verifies the state returns to "Fresh Session" with no history artifacts after reload.
