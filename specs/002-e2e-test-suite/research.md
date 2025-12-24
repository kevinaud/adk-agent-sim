# Research: E2E Test Suite

**Feature**: 002-e2e-test-suite  
**Date**: 2024-12-23 (Updated: 2025-12-23)  
**Purpose**: Resolve technical unknowns before implementation  
**Status**: ✅ Complete - All decisions confirmed by user

## Research Tasks

### 1. Playwright + NiceGUI Integration

**Question**: How do we run NiceGUI in "server mode" without spawning a desktop browser window?

**Research**: NiceGUI's `ui.run()` accepts several parameters to control its behavior:
- `native=False` - Prevents native desktop window (critical for containers)
- `show=False` - Prevents auto-opening browser
- `reload=False` - Disables hot-reload (required for stable test server)

**Decision**: ✅ CONFIRMED - Configure server with `ui.run(native=False, show=False, reload=False, port=8081)`

**Rationale**: These settings ensure NiceGUI runs as a pure web server, which Playwright can then connect to. Port 8081 avoids conflict with the dev server default (8080/8888).

**Alternatives Considered**:
- Using `ui.run(show=True)` with DISPLAY=:99 Xvfb → Rejected: Unnecessary complexity, headless browser handles this
- Mocking NiceGUI entirely → Rejected: Defeats purpose of E2E testing

---

### 2. Playwright Browser Installation in Dev Container

**Question**: How do we ensure Playwright browsers (Chromium) and their system dependencies are available in the Dev Container?

**Research**: Playwright requires specific system libraries (libgtk, libnss, etc.) that aren't in the base Python container.

**Decision**: ✅ CONFIRMED - Update `postCreateCommand` in devcontainer.json to run `uv sync && uv run playwright install --with-deps`

**Rationale**: 
- `--with-deps` installs the necessary system libraries via apt-get
- Running via `uv run` ensures it uses the project's virtual environment
- Constitution Principle VI mandates all deps in dev container, not manual setup

**Alternatives Considered**:
- Pre-built container image with Playwright → Rejected: Adds maintenance burden for custom image
- Installing via apt-get separately → Rejected: `playwright install --with-deps` is the canonical way

---

### 3. Server Lifecycle Management in pytest

**Question**: How do we start/stop the NiceGUI server reliably for E2E tests?

**Research**: Options considered:
1. subprocess.Popen - Start server as separate process
2. threading.Thread - Run server in background thread
3. multiprocessing.Process - Run in separate process with better isolation

**Decision**: ✅ CONFIRMED - Use `threading.Thread` with daemon=True to run the NiceGUI server

**Rationale**:
- Simpler than multiprocessing (no pickling issues with ADK agents)
- Daemon thread auto-terminates when pytest exits
- NiceGUI's uvicorn server handles the async event loop internally
- Session-scoped fixture ensures server runs for entire test session
- User confirmed background thread approach for simplicity

**Implementation Pattern**:
```python
@pytest.fixture(scope="session")
def run_server():
    from tests.fixtures.agents.test_agent.agent import get_test_agent
    from adk_agent_sim.simulator import AgentSimulator
    
    simulator = AgentSimulator(agents={"TestAgent": get_test_agent()}, port=8081)
    thread = threading.Thread(
        target=lambda: simulator._app.run(
            host="127.0.0.1",
            port=8081,
            native=False,
            show=False,
            reload=False,
        ),
        daemon=True,
    )
    thread.start()
    # Wait for server to be ready
    time.sleep(2)  # Or better: poll until responsive
    yield "http://127.0.0.1:8081"
    # Daemon thread auto-terminates
```

**Alternatives Considered**:
- Per-test server restart → Rejected: Too slow, introduces flakiness
- Manual server start before test run → Rejected: Violates FR-003 (auto-start)

---

### 4. Test Agent Strategy

**Question**: Does the existing demo agent have tools that exhibit all required schema types (boolean, enum, string, number)?

**Research**: Current demo agent in `agent.py`:
- `add(a: int, b: int)` - Two integer parameters ✅
- MCP server connection for additional tools

**Gap Identified**: Need tools with:
- Boolean parameter (for checkbox test)
- Enum parameter (for dropdown test)
- Error-throwing tool (for TC-03)

**Decision**: ✅ CONFIRMED - Create a dedicated `test_agent` in `tests/fixtures/agents/test_agent/`

**Rationale**: 
- The E2E tests need predictable tool schemas
- Modifying the demo agent could break other uses
- Test agent isolated from production code per clarification decisions
- Uses only local `FunctionTool` definitions (no MCP server dependency)

**Test Agent Tools**:
1. `add_numbers(a: int, b: int) -> int` - Basic happy path (number inputs)
2. `greet(name: str, formal: bool) -> str` - String + Boolean inputs
3. `get_status(level: Literal["low", "medium", "high"]) -> str` - Enum input
4. `fail_always() -> str` - Raises exception for error testing (TC-03)

---

### 5. NiceGUI Element Selectors for Playwright

**Question**: How do we reliably select NiceGUI elements with Playwright?

**Research**: NiceGUI generates elements with:
- Quasar/Vue.js components (q-input, q-select, q-btn, etc.)
- Auto-generated IDs or no IDs
- Custom classes can be added via `.classes()`

**Decision**: ✅ Use a combination of:
1. CSS selectors for Quasar components (`[class*="q-input"]`, `[class*="q-select"]`)
2. Text-based selectors for buttons (`text="Execute"`, `text="Start Session"`)
3. Role-based selectors where possible (`role=checkbox`, `role=textbox`)
4. Add `data-testid` attributes to critical elements for stable selectors

**Rationale**: 
- Quasar class selectors work for component type detection (TC-02)
- Text selectors are readable and match user perspective
- data-testid attributes can be added incrementally if flakiness occurs

**Alternatives Considered**:
- XPath selectors → Rejected: Brittle, hard to maintain
- Only data-testid → Rejected: Requires modifying all UI components first

---

### 6. Waiting Strategy for Async UI Updates

**Question**: How do we handle NiceGUI's async rendering in tests?

**Research**: NiceGUI uses websockets to push UI updates. Elements may not appear immediately after actions.

**Decision**: ✅ Use Playwright's built-in auto-waiting with explicit waits where needed

**Pattern**:
```python
# Auto-waiting (preferred)
page.click("text=Execute")  # Waits for element to be clickable

# Explicit wait for dynamic content
page.wait_for_selector("[class*='q-card']:has-text('Tool Output')", timeout=10000)

# Wait for network idle after navigation
page.wait_for_load_state("networkidle")
```

**Rationale**: 
- Playwright's auto-waiting handles 90% of cases
- Explicit waits only needed for dynamic content like history entries
- 10-second default timeout is reasonable for tool execution

---

### 7. Agent Configuration via Environment Variable

**Question**: How should the application be configured to use the `test_agent` during tests?

**Decision**: ✅ CONFIRMED - Set `ADK_AGENT_MODULE` environment variable via pytest configuration

**Implementation**:
```python
# tests/e2e/conftest.py
import os
os.environ["ADK_AGENT_MODULE"] = "tests.fixtures.agents.test_agent"
```

**Rationale**:
- Non-invasive: no code changes to application required
- Standard pytest pattern
- Clear separation between test and production configurations

---

### 8. Dependency Management

**Decision**: ✅ CONFIRMED - Add `pytest-playwright` as dev dependency via `uv`

**Command**:
```bash
uv add --dev pytest-playwright
```

**Rationale**: Constitution mandates `uv` for all dependency management. `pytest-playwright` includes `playwright` as transitive dependency.

---

## Summary of Decisions

| Unknown | Decision | Status |
|---------|----------|--------|
| NiceGUI server mode | `native=False, show=False, reload=False` | ✅ Confirmed |
| Playwright install | `uv sync && uv run playwright install --with-deps` in postCreateCommand | ✅ Confirmed |
| Server lifecycle | Session-scoped fixture with daemon Thread | ✅ Confirmed |
| Test agent location | `tests/fixtures/agents/test_agent/` | ✅ Confirmed |
| Test agent tools | Local FunctionTool only (no MCP) | ✅ Confirmed |
| Agent config | `ADK_AGENT_MODULE` env var via pytest | ✅ Confirmed |
| Element selection | CSS/text/role selectors, add data-testid as needed | ✅ Confirmed |
| Async handling | Playwright auto-wait + explicit waits for history | ✅ Confirmed |
| Dependencies | `uv add --dev pytest-playwright` | ✅ Confirmed |
| Execution command | `uv run pytest tests/e2e/` | ✅ Confirmed |
