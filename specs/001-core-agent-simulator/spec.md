# Feature Specification: Core Agent Simulator

**Feature Branch**: `001-core-agent-simulator`  
**Created**: 2025-12-22  
**Status**: Draft  
**Input**: User description: "ADK Agent Simulator - A Wizard of Oz human-in-the-loop tool for debugging agentic AI systems"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Roleplay as Agent to Debug Tools (Priority: P1)

As a developer debugging an agentic AI system, I want to "roleplay" as my ADK agent by seeing exactly what the agent sees (instructions, available tools) and manually executing tools via a UI, so I can determine whether failures are due to insufficient tools/context or model limitations.

**Why this priority**: This is the core value proposition. Without this capability, the product has no purpose. It directly addresses the problem of distinguishing between model failures, context failures, and tool failures.

**Independent Test**: Can be fully tested by loading a single ADK agent with tools, viewing its instructions, selecting a tool, filling in parameters via dynamic form, executing it, and seeing the output. Delivers immediate debugging value.

**Acceptance Scenarios**:

1. **Given** I have an ADK agent with tools defined, **When** I pass it to AgentSimulator and run the UI, **Then** I see the agent's name, description, and system instructions displayed prominently
2. **Given** the UI is loaded with an agent, **When** I view the tool list, **Then** I see all tools retrieved via `agent.canonical_tools()` with their names and descriptions
3. **Given** I select a tool from the list, **When** the tool form renders, **Then** I see dynamically generated input widgets matching the tool's parameter schema (STRING→text_input, INTEGER→number_input, BOOLEAN→checkbox, ENUM→selectbox)
4. **Given** I have filled in tool parameters, **When** I click "Run Tool", **Then** the tool executes via `tool.run_async()` and the output is displayed

---

### User Story 2 - Record Golden Traces for Evaluation (Priority: P2)

As a developer who successfully solved a task manually, I want to record my step-by-step tool executions as a "Golden Trace" JSON file, so I can use it as ground-truth for evaluating whether my LLM agent can replicate the solution.

**Why this priority**: This extends the debugging capability into a reusable artifact. Once a developer proves a task is solvable, they need to capture that proof for automated evaluation.

**Independent Test**: Can be tested by completing a multi-step task (entering user query, executing multiple tools, providing final response) and downloading the resulting JSON trace file. Validates the complete session recording workflow.

**Acceptance Scenarios**:

1. **Given** I start a new session, **When** I enter a user query, **Then** the query is recorded as the first event in the session history
2. **Given** I execute tools during a session, **When** each tool completes, **Then** the tool call (name, arguments) and output are appended to the history log
3. **Given** I have completed solving the task, **When** I click "End Turn" and type a final response, **Then** the final answer is recorded in the trace
4. **Given** a completed session exists, **When** I click "Download Trace", **Then** I receive a JSON file with metadata (agent_name, timestamp, user_query) and a trace array of steps

---

### User Story 3 - Switch Between Multiple Agents (Priority: P3)

As a developer with multiple agents in my project, I want to toggle between them in the simulator UI, so I can debug different agents without restarting the application.

**Why this priority**: Improves developer experience for complex projects but is not essential for core debugging functionality. Single-agent support delivers the primary value.

**Independent Test**: Can be tested by passing multiple agents to AgentSimulator, using a dropdown/sidebar to switch agents, and verifying that tools and instructions update accordingly.

**Acceptance Scenarios**:

1. **Given** I provide multiple agents to AgentSimulator, **When** the UI loads, **Then** I see a selector (dropdown or sidebar) listing all agent names
2. **Given** multiple agents are available, **When** I select a different agent, **Then** the displayed instructions, tools, and forms update to reflect the selected agent
3. **Given** I switch agents mid-session, **When** I view the history, **Then** the previous session is cleared or archived

---

### Edge Cases

- What happens when an agent has no tools attached? → Display a message: "This agent has no tools configured"
- What happens when tool execution raises an exception? → Catch and display as "Tool Error" output, mimicking how an LLM would receive an error frame
- What happens when a tool has complex/nested object parameters? → Render as st.text_area expecting JSON input
- What happens when required fields are not filled? → Disable "Run Tool" button and show validation messages
- How does the system handle async tool execution in Streamlit's sync environment? → Use `_run_async()` helper with proper event loop bridging

## Requirements *(mandatory)*

### Functional Requirements

- **FR-01**: System MUST expose a main class `AgentSimulator(agents: dict[str, Agent])` as the entry point
- **FR-02**: System MUST allow user selection between agents via sidebar or dropdown when multiple agents are provided
- **FR-03**: System MUST display agent name, description, and system instructions (via `agent.canonical_instruction()`) prominently
- **FR-04**: System MUST asynchronously retrieve tools via `agent.canonical_tools()` and display them
- **FR-05**: System MUST extract tool schemas via `tool._get_declaration()` to obtain FunctionDeclaration
- **FR-06**: System MUST dynamically generate Streamlit forms mapping parameter types to widgets:
  - STRING → st.text_input
  - INTEGER/NUMBER → st.number_input
  - BOOLEAN → st.checkbox
  - ENUM → st.selectbox
  - Complex/Nested Objects → st.text_area (parsed as JSON)
- **FR-07**: System MUST enforce basic type constraints and required field validation before execution
- **FR-08**: System MUST construct valid ToolContext and InvocationContext objects for ADK tool execution
- **FR-09**: System MUST provide mechanism to run async `tool.run_async()` within Streamlit's sync environment
- **FR-10**: System MUST catch tool execution exceptions and display them as "Tool Error" output
- **FR-11**: System MUST allow user to define initial User Query for a session
- **FR-12**: System MUST display chronological history log: User Message → Tool Call (inputs) → Tool Output
- **FR-13**: System MUST provide "End Turn" / "Submit Final Response" action for completing a session
- **FR-14**: System MUST allow downloading completed session as JSON file
- **FR-15**: Exported JSON MUST follow Golden Trace schema compatible with ADK evaluation tools

### Key Entities

- **AgentSimulator**: Main class that wraps ADK agents and launches Streamlit UI
- **Session**: Represents a single debugging run with user query, tool executions, and final response
- **GoldenTrace**: JSON export format containing metadata and step-by-step trace array
- **ToolContext**: ADK context object required for tool execution (must be mocked/constructed)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can load an ADK agent and view all its tools within 5 seconds of launching
- **SC-002**: Developer can execute any tool and see results within the tool's normal execution time + 1 second overhead
- **SC-003**: 100% of tool parameter types are correctly mapped to appropriate Streamlit widgets
- **SC-004**: Exported Golden Trace JSON passes schema validation for ADK evaluation compatibility
- **SC-005**: Developer can complete a 5-step debugging session and export trace in under 10 minutes
