# Feature Specification: Simulator Run

**Feature Branch**: `001-simulator-run`  
**Created**: 2025-12-23  
**Status**: Draft  
**Input**: User description: "Core workflow where a user simulates an agent's execution path"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute a Simple Tool Call (Priority: P1)

A developer wants to simulate their agent executing a single tool to understand how the agent would process a user query. They select a tool, fill in parameters using a dynamically-generated form, and execute it against the real tool implementation.

**Why this priority**: This is the atomic operation of the entire simulator. Without the ability to execute a single tool with correct parameter handling, no other features are possible.

**Independent Test**: Can be fully tested by providing an Agent with one tool, rendering its form, filling in values, executing, and verifying the output is displayed. Delivers immediate value by proving ADK integration works.

**Acceptance Scenarios**:

1. **Given** an Agent with a tool `add(a: int, b: int) -> int`, **When** the user selects `add`, fills in `a=5` and `b=3`, and clicks "Execute", **Then** the output `8` is displayed in the history log. The output MUST be obtained by executing the real tool in the same way that the ADK runtime
would execute it.

2. **Given** an Agent with a tool `search(query: str, limit: int = 10)`, **When** the UI renders the form, **Then** `query` is shown as a required text input and `limit` is shown as an optional number input with default value `10`.

3. **Given** an Agent with a tool that has an enum parameter `format: Literal["json", "xml"]`, **When** the UI renders the form, **Then** a dropdown/select widget is displayed with options `["json", "xml"]`.

---

### User Story 2 - Complete a Multi-Step Simulation Session (Priority: P1)

A developer wants to roleplay as an agent solving a user query that requires multiple tool calls. They start with an initial query, execute several tools in sequence, view the accumulated history, and then submit a final response.

**Why this priority**: This is the core "Wizard of Oz" workflow. It validates that session state is maintained correctly and that the human can see enough context to make informed decisions.

**Independent Test**: Can be fully tested by starting a session with a query, executing 2+ tools, verifying history shows all steps, then submitting a final response. Delivers the primary product value.

**Acceptance Scenarios**:

1. **Given** a fresh session, **When** the user enters "Calculate 5 * 5 + 10" as the initial query, **Then** the query is displayed as the first entry in the history log.

2. **Given** a session with one tool execution in history, **When** the user executes another tool, **Then** both tool calls and their outputs appear chronologically in the history.

3. **Given** a session with multiple tool calls in history, **When** the user clicks "Send Final Response" and enters "The answer is 35", **Then** the session ends and the final response is recorded.

---

### User Story 3 - Export Golden Trace (Priority: P1)

A developer has completed a simulation session and wants to export it as a Golden Trace JSON file for use with ADK evaluation tools.

**Why this priority**: The Golden Trace is the primary output artifact of the tool. Without export, the entire workflow produces nothing persistent.

**Independent Test**: Can be fully tested by completing a minimal session (1 query, 1 tool call, 1 final response), exporting, and validating the JSON structure matches ADK `EvalCase` schema.

**Acceptance Scenarios**:

1. **Given** a completed session with query "What is 2+2?", tool call `add(a=2, b=2)` returning `4`, and final response "The answer is 4", **When** the user exports, **Then** a JSON file is generated containing:
   - `eval_id`: A unique identifier
   - `conversation`: A list with one `Invocation` object
   - `Invocation.user_content`: Contains "What is 2+2?"
   - `Invocation.final_response`: Contains "The answer is 4"
   - `Invocation.intermediate_data.tool_uses`: Contains the `FunctionCall` for `add`
   - `Invocation.intermediate_data.tool_responses`: Contains the `FunctionResponse` with result `4`

2. **Given** a completed session, **When** the exported JSON is loaded into ADK's evaluation framework, **Then** it parses without errors as a valid `EvalCase`.

---

### User Story 4 - Handle Structured Input/Output Schemas (Priority: P2)

A developer has an Agent with a defined Pydantic `input_schema` and/or `output_schema`. The UI must render forms to collect structured input and validate the final response against the output schema.

**Why this priority**: Many production ADK agents use typed schemas. This is important for real-world usage but not required for the core loop to function.

**Independent Test**: Can be tested by providing an Agent with `input_schema=QueryInput` and `output_schema=StructuredResult`, verifying forms render correctly, and validating schema enforcement.

**Acceptance Scenarios**:

1. **Given** an Agent with `input_schema` defining `{"query": str, "max_results": int}`, **When** starting a new session, **Then** the UI renders a form with fields for `query` (text) and `max_results` (number) instead of a plain text input.

2. **Given** an Agent with `output_schema` defining `{"answer": str, "confidence": float}`, **When** the user clicks "Send Final Response", **Then** the UI renders a form requiring `answer` and `confidence` fields.

3. **Given** an Agent with `output_schema`, **When** the user submits a final response missing required fields, **Then** validation fails and the user is prompted to complete the form.

---

### User Story 5 - Handle Tool Execution Errors Gracefully (Priority: P2)

A developer executes a tool that throws an exception (e.g., network error, invalid API key, bad input). The error must be captured and displayed in the history so the developer can decide how to proceed.

**Why this priority**: Error handling is essential for real-world tool debugging, but the happy path must work first.

**Independent Test**: Can be tested by providing a tool that deliberately throws an exception, executing it, and verifying the error appears in the history log.

**Acceptance Scenarios**:

1. **Given** a tool `fetch_data(url: str)` that raises `ConnectionError`, **When** the user executes it, **Then** the history shows a "Tool Error" entry containing the exception type and message.

2. **Given** a tool error has occurred, **When** the user views the history, **Then** they can continue the session by executing another tool or submitting a final response.

3. **Given** a tool error occurs, **When** the Golden Trace is exported, **Then** the error is represented as a `FunctionResponse` with an error payload (not omitted).

---

### Edge Cases

- **Empty tool list**: What happens when an Agent has no tools? The UI must still allow submitting a final response directly.
- **Nested/complex parameters**: How does the UI handle tools with deeply nested object parameters? (Answer: Recursively rendered nested forms matching the schema structure)
- **Large tool output**: What if a tool returns megabytes of data? (Answer: Truncate display, full data in export)
- **Session abandonment**: What if the user closes the browser mid-session? (Answer: Session state should be recoverable or clearly marked as incomplete)
- **Concurrent tool execution**: Can the user execute multiple tools simultaneously? (Answer: No, tools execute sequentially per Wizard of Oz model)

## Requirements *(mandatory)*

### Functional Requirements

#### Dynamic Form Generation

- **FR-001**: System MUST inspect the Agent's available tools via `agent.canonical_tools()`.
- **FR-002**: System MUST retrieve each tool's schema via `tool._get_declaration()` returning a `FunctionDeclaration`.
- **FR-003**: System MUST dynamically render input forms based on `FunctionDeclaration.parameters` schema.
- **FR-004**: System MUST map schema types to appropriate UI widgets:
  - `STRING` → text input
  - `INTEGER` / `NUMBER` → number input
  - `BOOLEAN` → checkbox
  - `ENUM` → dropdown/select
  - `OBJECT` → recursively rendered nested form with fields for each property
  - `ARRAY` → dynamic list widget allowing add/remove of items, with each item rendered according to the array's `items` schema
- **FR-005**: System MUST display parameter descriptions from the schema to guide user input.
- **FR-006**: System MUST enforce `required` field constraints before allowing execution.

#### Simulation Workflow

- **FR-007**: System MUST allow user to provide an initial "User Query" to start a session.
- **FR-008**: System MUST render a structured input form if the Agent defines an `input_schema`.
- **FR-009**: System MUST display the conversation history including all prior steps.
- **FR-010**: System MUST present two action choices at each step: "Call a Tool" or "Send Final Response".
- **FR-011**: System MUST execute the actual underlying tool code via `tool.run_async()`.
- **FR-012**: System MUST capture and display tool outputs in the history.
- **FR-013**: System MUST render a structured output form if the Agent defines an `output_schema`.
- **FR-014**: System MUST validate final response against `output_schema` if defined.

#### History & Context

- **FR-015**: System MUST maintain a persistent, chronological session log.
- **FR-016**: History MUST display: user query, each tool invocation (name + inputs), each tool output, and final response.
- **FR-017**: History entries MUST be visually distinguishable by type (user input, tool call, tool output, final response, error).

#### Golden Trace Export

- **FR-018**: System MUST generate a JSON export upon session completion.
- **FR-019**: Exported JSON MUST conform to ADK `EvalCase` Pydantic model structure.
- **FR-020**: Export MUST include `eval_id` (unique identifier for the evaluation case).
- **FR-021**: Export MUST include `conversation` as a list of `Invocation` objects.
- **FR-022**: Each `Invocation.user_content` MUST contain the user query as `genai_types.Content`.
- **FR-023**: Each `Invocation.final_response` MUST contain the human's final answer as `genai_types.Content`.
- **FR-024**: Each `Invocation.intermediate_data` MUST be an `IntermediateData` object containing:
  - `tool_uses`: Chronological list of `genai_types.FunctionCall`
  - `tool_responses`: Chronological list of `genai_types.FunctionResponse`
- **FR-025**: Export MUST include `creation_timestamp` for the session.

#### Error Handling

- **FR-026**: System MUST catch exceptions raised during tool execution.
- **FR-027**: System MUST display tool errors in the history with exception type and message.
- **FR-028**: System MUST allow the session to continue after a tool error.
- **FR-029**: Tool errors MUST be represented in the Golden Trace export as `FunctionResponse` objects with error payloads.

#### Context Construction

- **FR-030**: System MUST construct a valid `ToolContext` for tool execution.
- **FR-031**: System MUST construct a valid `InvocationContext` as required by ADK tool methods.

### Key Entities

- **Session**: Represents a single simulation run. Contains the agent reference, conversation history, and state (active/completed).
- **HistoryEntry**: A single event in the session timeline. Discriminated union of: UserQuery, ToolCall, ToolOutput, ToolError, FinalResponse.
- **ToolCall**: Records a tool invocation. Contains tool name, input arguments, timestamp.
- **ToolOutput**: Records a tool's return value. Contains result data, timestamp, duration.
- **ToolError**: Records a failed tool execution. Contains exception type, message, traceback.
- **GoldenTrace**: The exportable `EvalCase`-compatible JSON structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can complete a simulation session (query → tool calls → final response) in under 5 minutes for a typical 3-tool workflow.
- **SC-002**: Exported Golden Traces parse successfully as valid `EvalCase` objects using ADK's Pydantic model 100% of the time.
- **SC-003**: All tool parameter types from `FunctionDeclaration` (STRING, INTEGER, NUMBER, BOOLEAN, ENUM, OBJECT, ARRAY) render correctly in the UI.
- **SC-004**: Tool execution errors are captured and displayed with sufficient detail to diagnose the issue (exception type + message at minimum).
- **SC-005**: Session history correctly reflects all operations in chronological order with no missing or duplicate entries.

## Constitution Compliance

This specification complies with the adk_agent_sim Constitution v1.1.0:

| Principle | Compliance |
|-----------|------------|
| I. Library-First | ✅ Feature is part of the library, not a standalone app |
| II. Wrapper Integration | ✅ Works with user-provided Agent instances |
| III. Wizard of Oz | ✅ Human manually decides tool calls and final response |
| IV. ADK Dependency | ✅ Uses `canonical_tools()`, `FunctionDeclaration`, `run_async()` |
| V. Golden Trace | ✅ Exports `EvalCase`-compatible JSON |
| VI. Hermetic Environment | ✅ No manual setup required (deferred to plan) |
| VII. Strict Standards | ✅ Implementation will follow Python 3.14+, ruff, pyright |
| VIII. Flexible UI | ✅ Spec is UI-framework-agnostic |
