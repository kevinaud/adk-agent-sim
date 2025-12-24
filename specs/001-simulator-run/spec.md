# Feature Specification: Simulator Run

**Feature Branch**: `001-simulator-run`  
**Created**: 2025-12-23  
**Status**: Draft  
**Input**: User description: "Core workflow where a user simulates an agent's execution path"

## Clarifications

### Session 2025-12-23
- Q: When a user closes the browser or navigates away mid-session, how should the simulator handle incomplete sessions? → A: **Ephemeral sessions only** - Sessions exist only in memory; closing browser loses all state. No persistence.
- Q: How should the `eval_id` (required for the Golden Trace export) be generated? → A: **Agent Name + Timestamp** - Format: `{snake_case_agent_name}_{iso_timestamp}` (e.g., `math_agent_2025-12-23T14:30:00`).
- Q: The `AgentSimulator` accepts a dictionary of agents. How should the simulator handle multiple agents? → A: **Selection at Startup** - User selects ONE agent to simulate upon launching the UI; cannot switch mid-session.
- Q: How should the Agent's **System Instructions** (persona/prompt) be presented to the human wizard? → A: **Prominent but Collapsible** - Visible by default to guide roleplay, but can be collapsed to save space.
- Q: How should the simulator handle **tool timeouts**? → A: **Manual Abort** - No enforced timeout; show elapsed time and provide a "Cancel" button for the user.

### Session 2025-12-24
- Q: How should agents be configured for the simulator? → A: **SimulatedAgentConfig** - Agents are provided as a list of `SimulatedAgentConfig` objects containing `name`, `agent`, and `eval_set_path` (the file path where completed eval cases should be appended).
- Q: Should we export individual EvalCase JSON files or use EvalSet files? → A: **EvalSet files** - The ADK `adk eval` CLI requires EvalSet files (which contain a list of EvalCases). Export should append to an existing EvalSet file or create a new one if it doesn't exist.
- Q: How should the `eval_set_path` be interpreted (absolute vs relative)? → A: **Relative to working directory** - If a relative path is provided, it is resolved relative to the current working directory where the simulator is launched. Absolute paths are used as-is.

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

### User Story 3 - Export Golden Trace to EvalSet (Priority: P1)

A developer has completed a simulation session and wants to export it as a Golden Trace to an EvalSet file for use with ADK's `adk eval` CLI tool.

**Why this priority**: The Golden Trace is the primary output artifact of the tool. The EvalSet format is required by the ADK CLI, so exporting directly to this format eliminates manual file manipulation.

**Independent Test**: Can be fully tested by completing a minimal session (1 query, 1 tool call, 1 final response), exporting, and validating the EvalSet file is created/updated correctly.

**Acceptance Scenarios**:

1. **Given** a completed session with query "What is 2+2?", tool call `add(a=2, b=2)` returning `4`, and final response "The answer is 4", **When** the user clicks "Export", **Then** the EvalCase is appended to the EvalSet file specified in the agent's `eval_set_path` configuration, containing:
   - `eval_id`: A unique identifier
   - `conversation`: A list with one `Invocation` object
   - `Invocation.user_content`: Contains "What is 2+2?"
   - `Invocation.final_response`: Contains "The answer is 4"
   - `Invocation.intermediate_data.tool_uses`: Contains the `FunctionCall` for `add`
   - `Invocation.intermediate_data.tool_responses`: Contains the `FunctionResponse` with result `4`

2. **Given** the `eval_set_path` file does not exist, **When** the user exports, **Then** a new EvalSet file is created with the eval case as the first entry, and appropriate metadata (`eval_set_id`, `creation_timestamp`).

3. **Given** the `eval_set_path` file already exists with previous eval cases, **When** the user exports, **Then** the new eval case is appended to the existing `eval_cases` list without overwriting previous entries.

4. **Given** a completed session, **When** the EvalSet file is used with `adk eval agent_module eval_set.json`, **Then** the evaluation runs successfully without parsing errors.

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
- **Session abandonment**: What if the user closes the browser mid-session? (Answer: Session state is lost immediately; no persistence)
- **Concurrent tool execution**: Can the user execute multiple tools simultaneously? (Answer: No, tools execute sequentially per Wizard of Oz model)

## Requirements *(mandatory)*

### Functional Requirements

#### Dynamic Form Generation

- **FR-001**: System MUST inspect the Agent's available tools via `agent.canonical_tools()`.
- **FR-002**: System MUST retrieve each tool's schema via `tool._get_declaration()` returning a `FunctionDeclaration`.
- **FR-003**: System MUST dynamically render input forms based on `FunctionDeclaration.parameters`, which is a `google.genai.types.Schema` instance.
- **FR-004**: System MUST implement a universal `Schema → Form` renderer that maps `google.genai.types.Schema` instances to UI widgets based on the `Schema.type` field (`google.genai.types.Type` enum):
  - `Type.STRING` → text input
  - `Type.INTEGER` / `Type.NUMBER` → number input
  - `Type.BOOLEAN` → checkbox
  - `Type.STRING` with `Schema.enum` populated → dropdown/select
  - `Type.OBJECT` → recursively rendered nested form with fields for each `Schema.properties` entry
  - `Type.ARRAY` → dynamic list widget allowing add/remove of items, with each item rendered according to `Schema.items`
- **FR-005**: System MUST display `Schema.description` for each field to guide user input.
- **FR-006**: System MUST enforce `Schema.required` field constraints before allowing execution.

#### Agent Configuration

- **FR-007**: System MUST accept agents as a list of `SimulatedAgentConfig` objects, each containing:
  - `name`: Display name for the agent
  - `agent`: The ADK Agent instance
  - `eval_set_path`: File path (absolute or relative to CWD) where completed eval cases should be exported
- **FR-007a**: System MUST allow user to select a single Agent to simulate if multiple are provided. This selection happens once at startup.

#### Simulation Workflow
- **FR-008**: System MUST display the Agent's system instructions (retrieved via `agent.canonical_instruction()`) prominently in the UI. This section MUST be collapsible.
- **FR-009**: System MUST allow user to provide an initial "User Query" to start a session.
- **FR-010**: System MUST render a structured input form if the Agent defines an `input_schema` (Pydantic model). The Pydantic model MUST be converted to `google.genai.types.Schema` via `Schema.from_json_schema(JSONSchema.model_validate(Model.model_json_schema()))` and rendered using the same `Schema → Form` logic as tool parameters (FR-004).
- **FR-011**: System MUST display the conversation history including all prior steps.
- **FR-012**: System MUST present two action choices at each step: "Call a Tool" or "Send Final Response".
- **FR-013**: System MUST execute the actual underlying tool code via `tool.run_async()`.
- **FR-014**: System MUST capture and display tool outputs in the history.
- **FR-015**: System MUST render a structured output form if the Agent defines an `output_schema` (Pydantic model). The Pydantic model MUST be converted to `google.genai.types.Schema` and rendered using the same `Schema → Form` logic (FR-004).
- **FR-016**: System MUST validate final response against `output_schema` if defined.

#### History & Context

- **FR-017**: System MUST maintain a persistent, chronological session log.
- **FR-018**: History MUST display: user query, each tool invocation (name + inputs), each tool output, and final response.
- **FR-019**: History entries MUST be visually distinguishable by type (user input, tool call, tool output, final response, error).

#### Golden Trace Export (EvalSet Format)

- **FR-020**: System MUST provide an "Export" button (not download) upon session completion.
- **FR-021**: Export MUST write to the `eval_set_path` specified in the agent's `SimulatedAgentConfig`.
- **FR-022**: If the target EvalSet file does not exist, system MUST create a new file with:
  - `eval_set_id`: Generated from agent name (e.g., `math_agent_evals`)
  - `name`: Optional descriptive name (can be agent name)
  - `eval_cases`: List containing the new EvalCase
  - `creation_timestamp`: Current Unix timestamp
- **FR-023**: If the target EvalSet file exists, system MUST:
  - Load the existing EvalSet
  - Append the new EvalCase to the `eval_cases` list
  - Write the updated EvalSet back to the file
- **FR-024**: Each EvalCase MUST conform to ADK `EvalCase` Pydantic model structure.
- **FR-025**: Each EvalCase MUST include `eval_id` generated as `{snake_case_agent_name}_{iso_timestamp}` (e.g., `my_agent_2025-12-23T10:00:00`).
- **FR-026**: Each EvalCase MUST include `conversation` as a list of `Invocation` objects.
- **FR-027**: Each `Invocation.user_content` MUST contain the user query as `genai_types.Content`.
- **FR-028**: Each `Invocation.final_response` MUST contain the human's final answer as `genai_types.Content`.
- **FR-029**: Each `Invocation.intermediate_data` MUST be an `IntermediateData` object containing:
  - `tool_uses`: Chronological list of `genai_types.FunctionCall`
  - `tool_responses`: Chronological list of `genai_types.FunctionResponse`
- **FR-030**: Export MUST include `creation_timestamp` for the EvalCase.

#### Error Handling

- **FR-028**: System MUST catch exceptions raised during tool execution.
- **FR-029**: System MUST display tool errors in the history with exception type and message.
- **FR-030**: System MUST allow the session to continue after a tool error.
- **FR-031**: Tool errors MUST be represented in the Golden Trace export as `FunctionResponse` objects with error payload `{"error": {"type": str, "message": str}}`.
- **FR-032**: System MUST display a stopwatch/timer during tool execution showing elapsed time.
- **FR-033**: System MUST provide a "Cancel" or "Abort" button during tool execution to manually stop a long-running tool.

#### Context Construction

- **FR-034**: System MUST construct a valid `ToolContext` for tool execution.
- **FR-035**: System MUST construct a valid `InvocationContext` as required by ADK tool methods.

### Key Entities

- **SimulatedAgentConfig**: Configuration for an agent in the simulator. Contains `name` (display name), `agent` (ADK Agent instance), and `eval_set_path` (file path for EvalSet export).
- **SimulationSession**: Represents a single simulation run. Contains the agent reference, conversation history, and state (active/completed).
- **HistoryEntry**: A single event in the session timeline. Discriminated union of: UserQuery, ToolCall, ToolOutput, ToolError, FinalResponse.
- **ToolCall**: Records a tool invocation. Contains tool name, input arguments, timestamp.
- **ToolOutput**: Records a tool's return value. Contains result data, timestamp, duration.
- **ToolError**: Records a failed tool execution. Contains exception type, message, and optional traceback (see data-model.md).
- **GoldenTrace**: The exportable `EvalCase`-compatible JSON structure (built by `GoldenTraceBuilder`).
- **EvalSet**: ADK model containing a list of EvalCases. This is the file format required by `adk eval` CLI.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can complete a simulation session (query → tool calls → final response) in under 5 minutes for a typical 3-tool workflow.
- **SC-002**: Exported EvalSet files parse successfully using ADK's `EvalSet` Pydantic model and work with `adk eval` CLI 100% of the time.
- **SC-003**: All `google.genai.types.Type` values supported by `Schema` (STRING, INTEGER, NUMBER, BOOLEAN, OBJECT, ARRAY) plus enum detection render correctly in the UI.
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
