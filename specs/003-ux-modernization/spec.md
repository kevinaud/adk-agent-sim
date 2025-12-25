# Feature Specification: UX Modernization

**Feature Branch**: `003-ux-modernization`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "We are going to start a new effort related to modernizing the UX of this application. I want you to analyze and understand the existing specs, and then take a look at docs/screenshots to see the current UX, and then write a new specification that lays out how we take our current crappy UX and turn it into a great UX. We are trying to maintain feature parity with this effort, just focusing on UX"

## Clarifications

### Session 2025-12-23
- Q: Should we introduce a "Dark Mode"? → A: **No** - Focus on layout and usability improvements first. Keep the theme light/clean for now to minimize scope creep.
- Q: Can we change the navigation structure? → A: **Yes** - As long as the user can still get to Agent Selection and Simulation, the flow can be optimized (e.g., better transitions).
- Q: Do we need to support mobile layouts? → A: **Desktop First** - The primary user is a developer/wizard on a desktop. Mobile responsiveness is a "nice to have" but not a P1 requirement.
- Q: What layout should the "Control Panel" use? → A: **Right Sidebar** - Vertical layout to the right of the chat, optimizing for vertical form space.
- Q: Where should the System Instructions be placed? → A: **Expandable Header** - Located at the top of the chat view, pushing content down when expanded.
- Q: What content should be displayed on the Agent Cards? → A: **Name & Description** - Keep it clean; show the agent's name and description (if available).
- Q: How should the history be presented? → A: **Structured Event Stream** - Not a chat app. Use full-width, distinct blocks for each event type (Input, Tool, Output) to emphasize the sequence of data.
- Q: How should complex data (JSON) be displayed? → A: **Collapsible JSON Tree** - Use an interactive tree view to allow exploration of nested data without clutter.

### Session 2025-12-24
- Q: Should tool inputs/outputs be expanded or collapsed by default? → A: **Expanded by default** - Users need to see the full data without extra clicks. They can collapse if needed.
- Q: Should expanded/collapsed state persist across UI actions? → A: **Yes, session-only** - When the user expands/collapses a section, that state must persist within the current session (in-memory). State is NOT persisted across page refreshes or browser sessions.
- Q: Should there be bulk expand/collapse controls? → A: **Yes, per-event** - Each event block should have "Expand All" and "Collapse All" buttons to control all collapsible children within that event.
- Q: How should text data in tool outputs be displayed? → A: **Toggleable presentation modes** - Each text element should support three rendering modes: Raw (plain text), JSON (parsed/pretty-printed), and Markdown (rendered). Default is Raw, but auto-detect JSON and switch to JSON mode if parseable.
- Q: How should tool selection display tool information? → A: **Full tool catalog view** - Show all tools simultaneously with name, description, input schema, and output schema visible (using collapsible panels to manage space).
- Q: Why does "No description available" appear for agents with descriptions? → A: **Bug to fix** - The agent description is not being correctly retrieved from the Agent object. This must be fixed to display actual descriptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Modern Agent Selection Dashboard (Priority: P1)

A developer launches the application and is greeted by a visually appealing dashboard to select an agent, rather than a simple dropdown. This sets the tone for a polished experience.

**Why this priority**: First impressions matter. The entry point should feel like a professional tool.

**Independent Test**: Can be tested by launching the app and verifying the agent selection screen renders as a grid of cards.

**Acceptance Scenarios**:

1. **Given** the application start page, **When** the page loads, **Then** available agents are displayed as a grid of interactive cards showing **Name and Description**.
2. **Given** an agent that has a description defined in its configuration, **When** the agent card renders, **Then** the actual description text is displayed (NOT "No description available").
3. **Given** an agent that has no description defined, **When** the agent card renders, **Then** "No description available" is shown as fallback text.
4. **Given** the agent grid, **When** the user hovers over a card, **Then** it shows a visual elevation/highlight effect.
5. **Given** the agent grid, **When** the user clicks a card, **Then** the simulation session starts and navigates to the simulation view.

---

### User Story 2 - Structured Event Stream Interface (Priority: P1)

A developer is running a simulation. They see the session history presented as a structured stream of events (Input, Tool Execution, Output) rather than a conversational chat. This emphasizes the technical sequence and data flow.

**Why this priority**: The core value is the accurate recording of the agent's execution path. A structured view allows for better inspection of payloads and results.

**Independent Test**: Can be tested by running a simulation and verifying the history renders as distinct event blocks.

**Acceptance Scenarios**:

1. **Given** a simulation session, **When** the User (Wizard) provides input, **Then** it appears as a distinct "User Input" block with the full content visible.
2. **Given** a simulation session, **When** the Agent responds, **Then** it appears as a distinct "Agent Response" block.
3. **Given** a tool execution, **When** it appears in the history, **Then** it is rendered as a "Tool Execution" block showing the tool name, arguments, and result in a structured format (e.g., JSON view).
4. **Given** a tool call or tool output event, **When** it first renders, **Then** all collapsible sections (arguments, results) are **expanded by default**.
5. **Given** a user has collapsed a section in an event, **When** they perform another UI action (select tool, execute, etc.), **Then** the collapsed state is **preserved** and not reset.
6. **Given** a user has expanded a section in an event, **When** new events are added to the stream, **Then** the expanded state of existing events is **preserved**.
7. **Given** an event block with multiple collapsible sections, **When** the user views it, **Then** "Expand All" and "Collapse All" buttons are visible for that event.
8. **Given** an event block with some sections collapsed, **When** the user clicks "Expand All", **Then** all collapsible children within that event expand.
9. **Given** an event block with some sections expanded, **When** the user clicks "Collapse All", **Then** all collapsible children within that event collapse.

---

### User Story 3 - Integrated "Wizard" Control Panel (Priority: P2)

A developer needs to control the agent (execute tools, send messages). Instead of a split-screen that feels like two separate apps, the controls are integrated into a cohesive "Control Panel" or Sidebar that complements the event stream.

**Why this priority**: Improves the workflow efficiency. The controls should feel like an extension of the stream, not a separate form.

**Independent Test**: Can be tested by verifying the layout of the simulation page.

**Acceptance Scenarios**:

1. **Given** the simulation view, **When** the session is active, **Then** the "Action Panel" (Tool Selection / Message Input) is anchored to the **right sidebar** in a fixed, accessible area.
2. **Given** the tool selection state, **When** a tool is selected, **Then** the parameter form appears within the Control Panel without obscuring the event history.
3. **Given** the system prompt, **When** the user wants to view it, **Then** it is available via a **collapsible header** at the top of the view.

---

### User Story 4 - Enhanced Tool Execution Feedback (Priority: P2)

A developer executes a tool. The UI provides clear visual feedback during execution (loading states) and presents the results in a readable, formatted way (e.g., syntax highlighting for JSON).

**Why this priority**: Tool outputs can be complex. Raw text dumps are hard to read.

**Independent Test**: Can be tested by executing a tool that returns JSON or complex text.

**Acceptance Scenarios**:

1. **Given** a tool is executing, **When** waiting for the result, **Then** a clear loading indicator is shown in the event stream.
2. **Given** a tool returns JSON data, **When** the result is displayed in history, **Then** it is formatted as a **Collapsible JSON Tree** allowing the user to expand/collapse nested fields.
3. **Given** a tool error, **When** it occurs, **Then** it is displayed with a distinct "Error" style (red accent, warning icon) to be immediately recognizable.
4. **Given** a tool output contains a text field, **When** the result is displayed, **Then** a presentation toggle is visible allowing the user to switch between Raw, JSON, and Markdown modes.
5. **Given** a tool output contains a text field with valid JSON content, **When** the result is first displayed, **Then** the presentation mode is automatically set to JSON (pretty-printed).
6. **Given** a tool output contains a text field that is not valid JSON, **When** the result is first displayed, **Then** the presentation mode defaults to Raw.
7. **Given** a text field in JSON mode, **When** the user clicks the "Raw" toggle, **Then** the content switches to plain unformatted text.
8. **Given** a text field in any mode, **When** the user clicks the "Markdown" toggle, **Then** the content is rendered as Markdown.

---

### User Story 5 - Comprehensive Tool Selection Interface (Priority: P2)

A developer needs to select a tool to execute. Instead of a dropdown that only shows tool names, they see a catalog view displaying all available tools with full details (name, description, input schema, output schema) to make an informed decision.

**Why this priority**: AI agents have access to full tool metadata when selecting tools. The human wizard should have the same information to accurately emulate agent behavior.

**Independent Test**: Can be tested by verifying the tool selection UI displays all required tool metadata.

**Acceptance Scenarios**:

1. **Given** the tool selection phase, **When** the user views available tools, **Then** all tools are displayed simultaneously (not in a dropdown).
2. **Given** the tool catalog, **When** viewing a tool entry, **Then** the tool's **name** is prominently displayed.
3. **Given** the tool catalog, **When** viewing a tool entry, **Then** the tool's **description** is visible (if available).
4. **Given** the tool catalog, **When** viewing a tool entry, **Then** the tool's **input schema** is viewable (in a collapsible panel to save space).
5. **Given** the tool catalog, **When** viewing a tool entry, **Then** the tool's **output schema** is viewable (in a collapsible panel to save space).
6. **Given** the tool catalog with multiple tools, **When** viewing all tools, **Then** collapsible panels prevent the view from becoming overwhelming.
7. **Given** the tool catalog, **When** the user clicks on a tool, **Then** the tool is selected and the parameter input form is displayed.

---

### Edge Cases

- **Long History**: Event stream view must scroll automatically to the newest event but allow manual scrolling up.
- **Large Tool Outputs**: Very large text/JSON outputs should be truncated with a "Show More" option to prevent flooding the view.
- **Window Resize**: The layout should maintain usability (sidebar doesn't disappear, stream remains readable) on smaller desktop windows.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST use a consistent design system (colors, typography, spacing) that provides a modern, professional aesthetic.
- **FR-002**: The Agent Selection page MUST display agents in a Card Grid layout.
- **FR-002a**: Agent cards MUST display the actual agent description retrieved from the Agent object, not hardcoded fallback text.
- **FR-003**: The Simulation page MUST use a "Event Stream" layout (Vertical list of event blocks, Controls sidebar).
- **FR-004**: History events MUST be visually distinct based on the event type (User Input vs. Agent Response vs. Tool Execution).
- **FR-005**: Tool outputs and complex data MUST be rendered using an interactive **Collapsible JSON Tree** component.
- **FR-005a**: Collapsible sections in events MUST be **expanded by default** when first rendered.
- **FR-005b**: The expanded/collapsed state of event sections MUST be **preserved** within the current session (in-memory only; not persisted across page refresh).
- **FR-005c**: Each event block MUST include **"Expand All"** and **"Collapse All"** buttons to bulk-toggle all collapsible children.
- **FR-005d**: Each text data element MUST include a **presentation toggle** supporting three modes: **Raw**, **JSON**, and **Markdown**.
- **FR-005e**: The default presentation mode MUST be **Raw**, except when the content is valid JSON (object or array), in which case it MUST default to **JSON**.
- **FR-005f**: Text exceeding **500 characters** in Raw mode MUST be truncated with a "Show More" link to expand.
- **FR-006**: The System Prompt MUST be accessible but collapsible/hidden by default to save screen real estate.
- **FR-007**: The UI MUST provide visual feedback (spinners/loaders) for all async operations (connecting, executing tools).
- **FR-008**: All existing functionality (Select Agent, Run Tool, Send Message, Export Trace) MUST be preserved (Feature Parity).
- **FR-009**: Tool selection MUST display a **catalog view** showing all tools simultaneously with name, description, input schema, and output schema.
- **FR-009a**: Tool input/output schemas MUST be displayed in **collapsible panels** to manage vertical space.
- **FR-009b**: Tool selection MUST NOT use a dropdown that only shows tool names.

### Success Criteria

- **Visual Consistency**: All pages share the same color palette, typography, and component styling.
- **Readability**: Chat history is readable at a glance, with clear distinction between actors.
- **Usability**: Users can perform common actions (select tool, send message) with the same or fewer clicks than the previous version.
- **Parity**: 100% of the features defined in `001-simulator-run` are present and functional.
- **State Persistence**: Expand/collapse states and presentation mode selections are maintained within a session (not across page refresh).
- **Tool Visibility**: All tool metadata (name, description, schemas) is visible during tool selection.
- **Agent Descriptions**: Agents with descriptions defined display their actual description text on selection cards.

### Assumptions

- We are continuing to use NiceGUI as the framework.
- We can use standard Tailwind CSS classes for styling.
- No changes to the backend `SimulationController` or `Agent` models are required, only UI layer changes.
