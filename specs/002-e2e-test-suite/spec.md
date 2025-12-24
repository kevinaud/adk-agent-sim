# Feature Specification: E2E Test Suite

**Feature Branch**: `002-e2e-test-suite`  
**Created**: 2024-12-23  
**Status**: Draft  
**Input**: User description: "E2E Test Suite for Simulator Run feature using Playwright via pytest"

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2025-12-23
- Q: Should we modify the existing `demo_agent` or create a new one for testing? → A: Create a new dedicated `test_agent` specifically for E2E testing.
- Q: Should the `test_agent` use local tools or require a running MCP server? → A: Use local `FunctionTool` definitions only (no MCP server required).
- Q: How should the application be configured to use the `test_agent` during tests? → A: Configure `ADK_AGENT_MODULE` via `pytest` configuration (env var injection).
- Q: Where should the `test_agent` be located? → A: `tests/fixtures/agents/` (Separation of concerns, keeps source clean).
- Q: How should the test suite launch the application server? → A: Use a background thread with daemon=True (simpler than subprocess, avoids pickling issues with ADK agents, auto-terminates on pytest exit).

### User Story 1 - Execute Complete Simulation Flow (Priority: P1)

As a QA engineer or developer, I need to verify that the complete "Simulator Run" workflow functions correctly from start to finish when interacting with the running application in a browser.

**Why this priority**: This is the critical happy path that validates the core feature works. Without this working, all other test scenarios are meaningless.

**Independent Test**: Can be fully tested by running the automated test suite which launches the app, performs a complete simulation flow, and verifies each step produces expected results.

**Acceptance Scenarios**:

1. **Given** the NiceGUI application is running, **When** the test suite starts, **Then** Playwright can connect to the application and interact with UI elements.

2. **Given** a fresh application state, **When** a user enters a query and submits it, **Then** the system displays available tools for selection.

3. **Given** available tools are displayed, **When** a user selects a tool, **Then** a dynamic form renders with the appropriate input fields.

4. **Given** a tool form is displayed, **When** a user fills in the form and executes, **Then** the tool result appears in the history panel.

5. **Given** tool execution has completed, **When** a user submits a final response, **Then** the session completes successfully and history reflects the full conversation.

---

### User Story 2 - Verify Dynamic Form Rendering (Priority: P2)

As a QA engineer, I need to verify that different ADK schema types render the correct UI widgets so that users have appropriate input controls for each data type.

**Why this priority**: Dynamic form generation is a core architectural feature. If forms render incorrectly, users cannot provide proper tool inputs.

**Independent Test**: Can be tested by triggering tools with known schema types and asserting the correct widget types appear in the DOM.

**Acceptance Scenarios**:

1. **Given** a tool with a boolean parameter, **When** the form renders, **Then** a checkbox widget is displayed.

2. **Given** a tool with an enum parameter, **When** the form renders, **Then** a dropdown/select widget is displayed with the enum options.

3. **Given** a tool with a string parameter, **When** the form renders, **Then** a text input field is displayed.

4. **Given** a tool with a number parameter, **When** the form renders, **Then** a numeric input field is displayed.

---

### User Story 3 - Handle Tool Execution Errors Gracefully (Priority: P2)

As a QA engineer, I need to verify that when a tool throws an exception, the UI handles it gracefully, displays the error prominently, and allows the session to continue.

**Why this priority**: Error resilience is critical for user experience. Users must not lose their work when a tool fails.

**Independent Test**: Can be tested by executing a tool known to throw an exception and verifying the error display and session continuity.

**Acceptance Scenarios**:

1. **Given** a tool that will throw an exception, **When** the user executes the tool, **Then** the UI displays an error card with prominent styling (red/error color).

2. **Given** a tool has thrown an exception, **When** the error is displayed, **Then** the user can still interact with the application (select other tools, enter new queries).

3. **Given** an error has occurred, **When** the user continues the session, **Then** the error remains visible in the history for reference.

---

### User Story 4 - Verify State Isolation Between Sessions (Priority: P3)

As a QA engineer, I need to verify that sessions are ephemeral and state is properly cleared when starting fresh, ensuring no data leaks between sessions.

**Why this priority**: State isolation is important for security and predictability, but is less critical than core functionality.

**Independent Test**: Can be tested by performing actions, reloading the page, and verifying the state is cleared.

**Acceptance Scenarios**:

1. **Given** a session with existing history (queries, tool executions), **When** the page is reloaded, **Then** the previous state is cleared.

2. **Given** a session with existing history, **When** a new session is explicitly started, **Then** the previous state is cleared.

3. **Given** a fresh session, **When** the user inspects the UI, **Then** no artifacts from previous sessions are visible.

---

### User Story 5 - Capture UX Screenshots for Visual Analysis (Priority: P2)

As a developer or designer, I need the E2E test suite to capture screenshots of all major UX views and store them in the repository so that I can analyze visual quality, track UI changes over time, and enable AI assistants to provide feedback on the user interface.

**Why this priority**: Visual documentation enables code review of UX changes, supports AI-assisted design feedback, and creates a historical record of the interface evolution.

**Independent Test**: Can be verified by running the test suite and confirming screenshot files exist in the expected directory with appropriate naming.

**Acceptance Scenarios**:

1. **Given** the E2E test suite runs, **When** the agent selection page loads, **Then** a screenshot is captured and saved to `docs/screenshots/agent-selection.png`.

2. **Given** a simulation session is active, **When** the query input form is displayed, **Then** a screenshot is captured and saved to `docs/screenshots/query-input.png`.

3. **Given** tools are available for selection, **When** the action panel displays the tool list, **Then** a screenshot is captured and saved to `docs/screenshots/tool-selection.png`.

4. **Given** a tool is selected, **When** the dynamic parameter form renders, **Then** a screenshot is captured and saved to `docs/screenshots/tool-form.png`.

5. **Given** a tool has been executed, **When** the history panel shows the result, **Then** a screenshot is captured and saved to `docs/screenshots/tool-result.png`.

6. **Given** an error occurs during tool execution, **When** the error is displayed in the history, **Then** a screenshot is captured and saved to `docs/screenshots/error-display.png`.

7. **Given** a session is complete, **When** the final response is shown, **Then** a screenshot is captured and saved to `docs/screenshots/session-complete.png`.

**Screenshot Requirements**:
- Screenshots MUST be in PNG format for lossless quality
- Screenshots MUST use consistent naming convention: `kebab-case.png`
- Screenshots MUST be stored in `docs/screenshots/` directory
- Screenshots MUST be committed to the repository (not gitignored)
- Screenshots SHOULD be captured at a consistent viewport size (1280x720 recommended)
- Screenshots MUST be updated automatically when tests run successfully

---

### Edge Cases

- What happens when the NiceGUI server fails to start within the expected timeout? → **Handled**: pytest timeout fixture fails test with clear error message.
- How does the test suite handle flaky network conditions or slow rendering? → **Handled**: Playwright's built-in auto-waiting plus explicit waits for dynamic content.
- What happens when a tool has nested or complex schema types? → **Out of scope**: Initial suite tests basic types only (int, str, bool, enum).
- How does the system handle concurrent test execution? → **Handled**: Single-threaded execution (see Assumptions); no port conflicts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Test suite MUST use Playwright as the browser automation framework via pytest integration.
- **FR-002**: Tests MUST run in headless mode by default to support Dev Container and CI/CD environments.
- **FR-003**: Test suite MUST automatically start the NiceGUI server before tests run.
- **FR-004**: Test suite MUST automatically stop the NiceGUI server after all tests complete.
- **FR-005**: Tests MUST interact with the application as a black-box (no internal method calls or direct database access).
- **FR-006**: Test suite MUST include TC-01 (Happy Path) covering the complete simulation flow.
- **FR-007**: Test suite MUST include TC-02 (Dynamic Forms) verifying widget rendering for schema types (boolean→checkbox, enum→dropdown).
- **FR-008**: Test suite MUST include TC-03 (Error Handling) verifying error display and session continuity.
- **FR-009**: Test suite MUST include TC-04 (State Isolation) verifying ephemeral session behavior.
- **FR-010**: Tests MUST be fully automated with no manual intervention required.
- **FR-011**: Test suite MUST provide clear pass/fail reporting for each test case.
- **FR-012**: Tests MUST wait for UI elements appropriately to handle asynchronous rendering.
- **FR-013**: The `test_agent` MUST be configured using only local `FunctionTool` definitions to avoid external MCP server dependencies during testing.
- **FR-014**: The test environment MUST inject the `ADK_AGENT_MODULE` environment variable to point to the `test_agent` module before starting the application server.
- **FR-015**: The `test_agent` source code MUST be located in `tests/fixtures/agents/` and not included in the main application package.
- **FR-016**: The test suite MUST launch the application server in a background thread with `daemon=True` to ensure automatic cleanup and prevent asyncio event loop conflicts with the test runner.
- **FR-017**: The test suite MUST capture screenshots of all major UX views during test execution.
- **FR-018**: Screenshots MUST be saved to `docs/screenshots/` directory in PNG format.
- **FR-019**: Screenshots MUST use consistent kebab-case naming (e.g., `agent-selection.png`, `tool-form.png`).
- **FR-020**: Screenshots MUST be captured at a consistent viewport size of 1280x720 pixels.
- **FR-021**: The screenshot directory and files MUST be committed to version control (not gitignored).
- **FR-022**: Screenshots MUST be automatically updated when the E2E test suite runs successfully.
- **FR-023**: The test suite MUST capture at minimum: agent selection page, query input, tool selection, tool form, tool result, error display, and session completion views.

### Key Entities

- **Test Case**: A discrete, automated verification of a specific behavior. Contains setup, actions, and assertions.
- **Test Fixture**: Reusable setup/teardown logic for managing application lifecycle and browser sessions.
- **Page Object** (optional): Abstraction layer encapsulating UI element selectors and common interactions for maintainability.
- **UX Screenshot**: A PNG image file capturing a specific UI state, stored in `docs/screenshots/` for visual documentation and AI-assisted analysis.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 4 test cases (TC-01 through TC-04) pass consistently within the Dev Container environment.
- **SC-002**: Test suite completes execution within 5 minutes for the full suite.
- **SC-003**: Test suite requires zero manual clicks or interventions to run.
- **SC-004**: Test suite can be executed via a single command (e.g., \`pytest tests/e2e/\`).
- **SC-005**: Test failures produce actionable error messages identifying the failed assertion and relevant context.
- **SC-006**: Test suite achieves 100% pass rate on repeated runs (no flaky tests).
- **SC-007**: Screenshots of all 7 major UX views are captured and saved to `docs/screenshots/`.
- **SC-008**: Screenshots are readable and clearly show the UI state being documented.
- **SC-009**: Screenshots enable AI assistants to analyze and provide feedback on visual UX quality.

## Assumptions

- The NiceGUI application is configured to run on a predictable port (default or configurable).
- A dedicated `test_agent` is created specifically for E2E testing, configured with tools exhibiting required schema types (boolean, enum, string, number) and error behaviors.
- The Dev Container has all necessary dependencies (Playwright browsers, pytest) installed or installable.
- Tests run in a single-threaded manner to avoid port conflicts with the application server.
