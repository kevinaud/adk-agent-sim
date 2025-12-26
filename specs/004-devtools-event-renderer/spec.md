# Feature Specification: Compact DevTools-Style Event Stream Renderer

**Feature Branch**: `004-devtools-event-renderer`  
**Created**: 2025-12-26  
**Status**: Draft  
**Input**: User description: "Compact DevTools-Style Event Stream Renderer"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Execution Trace at a Glance (Priority: P1)

As a developer diagnosing agent behavior, I want to see the full execution trace immediately upon opening the event stream, so that I can quickly understand what happened without clicking through multiple layers of accordions.

**Why this priority**: This is the core value proposition. The current UI requires excessive clicking to reveal nested data, creating "Accordion Fatigue" that slows diagnosis. Immediate visibility of the data tree is the fundamental improvement.

**Independent Test**: Load an event with nested execution trace data and verify all nodes are expanded by default, displaying the full hierarchy without any user interaction.

**Acceptance Scenarios**:

1. **Given** an event stream containing a deeply nested execution trace (3+ levels), **When** the event renders, **Then** all tree nodes are expanded by default showing the complete data hierarchy.
2. **Given** an event with structured data (JSON objects/arrays), **When** viewing the event, **Then** the data displays as a compact hierarchical tree with proper indentation.
3. **Given** a tree structure with multiple nesting levels, **When** viewing the tree, **Then** thin vertical guide lines ("thread lines") connect parent nodes to their children for visual clarity.

---

### User Story 2 - Manage Large Data Trees (Priority: P1)

As a developer viewing a large execution trace, I want global controls to collapse or expand all nodes, so that I can quickly toggle between overview and detail views of the data.

**Why this priority**: Large datasets become overwhelming when fully expanded. Global controls complement the "expanded by default" behavior by giving users agency to manage the view.

**Independent Test**: Render a complex event trace, click "Collapse All", verify all nodes collapse; click "Expand All", verify all nodes expand.

**Acceptance Scenarios**:

1. **Given** a fully expanded data tree, **When** the user clicks "Collapse All", **Then** all expandable nodes collapse to show only top-level keys.
2. **Given** a fully collapsed data tree, **When** the user clicks "Expand All", **Then** all expandable nodes expand to show the complete hierarchy.
3. **Given** the event stream view, **When** looking for global controls, **Then** "Collapse All" and "Expand All" controls are accessible near the top of the view.

---

### User Story 3 - Inspect Embedded JSON Content (Priority: P2)

As a developer, when I encounter a string field that contains embedded JSON (e.g., a serialized config object), I want to expand it inline as a parsed tree, so that I can read the structured data without leaving the context.

**Why this priority**: Agent traces commonly include stringified JSON in fields like `remote_config`. Inline expansion eliminates context-switching and preserves the developer's mental model of the data hierarchy.

**Independent Test**: Render an event where a string value is `'{"model": "gemini-1.5-pro", "temperature": 0.7}'`, verify the `[JSON]` toggle appears, click it, and verify the content expands inline as a parsed tree.

**Acceptance Scenarios**:

1. **Given** a string value that starts with `{` or `[` and is valid JSON, **When** the tree renders, **Then** the system shows a truncated preview with a `[JSON]` toggle pill.
2. **Given** a string value with a `[JSON]` toggle, **When** the user clicks the toggle, **Then** the JSON is parsed and rendered inline as a recursive tree respecting parent indentation.
3. **Given** expanded inline JSON content, **When** the user clicks the toggle again (or a close control), **Then** the content collapses back to the truncated preview.

---

### User Story 4 - Inspect Embedded Markdown Content (Priority: P2)

As a developer, when I encounter a string field that contains Markdown (e.g., chain-of-thought reasoning), I want to render it as formatted Markdown inline, so that I can read it naturally without raw syntax cluttering the view.

**Why this priority**: Agent reasoning traces often include Markdown-formatted explanations. Rendering them properly improves readability significantly.

**Independent Test**: Render an event where a string value contains Markdown syntax (e.g., `**bold**` or bullet lists), verify the `[MD]` toggle appears, click it, and verify formatted Markdown renders inline.

**Acceptance Scenarios**:

1. **Given** a string value that contains Markdown indicators (headers, bold, lists, etc.), **When** the tree renders, **Then** the system shows a truncated preview with `[RAW]` and `[MD]` toggle pills.
2. **Given** a string value with an `[MD]` toggle, **When** the user clicks the toggle, **Then** the Markdown is rendered inline with proper formatting (bold, lists, headers, etc.).
3. **Given** rendered Markdown content, **When** the user clicks `[RAW]`, **Then** the content switches to display the raw string without Markdown processing.

---

### User Story 5 - View Raw String Content (Priority: P2)

As a developer, when viewing any string field, I want the option to see the raw content, so that I can inspect the exact data when debugging parsing or encoding issues.

**Why this priority**: Sometimes developers need to see exact string content including escape sequences, whitespace, and special characters.

**Independent Test**: Render an event with a multi-line string, verify `[RAW]` toggle is available, click it, and verify the raw string displays preserving newlines and whitespace.

**Acceptance Scenarios**:

1. **Given** any string value, **When** the tree renders, **Then** a `[RAW]` toggle is available to view the unprocessed string content.
2. **Given** a multi-line string displayed via `[RAW]`, **When** viewing the content, **Then** newlines and whitespace are preserved exactly as in the source data.
3. **Given** a string currently showing formatted view (JSON or MD), **When** the user clicks `[RAW]`, **Then** the view switches to show the original raw string.

---

### User Story 6 - Visual Aesthetic Matches DevTools (Priority: P3)

As a developer accustomed to browser DevTools or IDE interfaces, I want the event stream to use similar visual conventions, so that it feels familiar and enables rapid scanning of data.

**Why this priority**: Visual familiarity reduces cognitive load. Developers already trained on DevTools patterns can immediately apply their existing mental models.

**Independent Test**: Compare rendered output visually against reference (attached screenshot), verify monospace typography, syntax coloring, minimal padding, and no heavy borders.

**Acceptance Scenarios**:

1. **Given** a rendered data tree, **When** inspecting the typography, **Then** keys and values use monospace font with distinct syntax colors (e.g., keys in one color, string values in another).
2. **Given** a rendered data tree, **When** inspecting layout, **Then** the design uses minimal padding and avoids heavy borders or box elements.
3. **Given** nested data, **When** inspecting visual hierarchy, **Then** indentation is consistent and thread lines provide clear parent-child relationships.

---

### Edge Cases

- What happens when a string looks like JSON but is malformed? → System should gracefully fall back to RAW view and not offer JSON toggle, or show an error state if toggle was clicked.
- What happens when a string is extremely long (10KB+)? → System should truncate the preview and render expanded content performantly (consider virtualization for very large content).
- What happens when nested JSON contains another stringified JSON (double-encoded)? → The recursive parser should detect and offer toggles for nested stringified content.
- What happens when data contains circular references? → System should detect and handle gracefully without infinite loops.
- What happens when Markdown detection has false positives (e.g., string contains `*` but isn't Markdown)? → The toggle approach allows users to choose RAW if MD rendering is unhelpful.

## Requirements *(mandatory)*

### Functional Requirements

**Tree Rendering Core**
- **FR-001**: System MUST render JSON objects and arrays as a hierarchical tree structure with collapsible nodes.
- **FR-002**: System MUST expand all tree nodes by default when initially rendering.
- **FR-003**: System MUST display thin vertical guide lines (thread lines) connecting parent nodes to their children.
- **FR-004**: System MUST use monospace typography for tree content.
- **FR-005**: System MUST apply syntax coloring to distinguish keys from values (distinct colors for keys vs. string/number/boolean values).
- **FR-006**: System MUST use minimal padding and avoid heavy borders to achieve high information density.

**Global Controls**
- **FR-007**: System MUST provide a "Collapse All" control that collapses all expandable nodes in the current event view.
- **FR-008**: System MUST provide an "Expand All" control that expands all expandable nodes in the current event view.
- **FR-009**: Global controls MUST be accessible near the top of the event view.

**Smart Blob Detection - JSON**
- **FR-010**: System MUST detect string values that contain valid JSON (strings starting with `{` or `[` that parse successfully).
- **FR-011**: System MUST display detected JSON blobs with a truncated preview and a `[JSON]` toggle pill.
- **FR-012**: When user activates `[JSON]` toggle, system MUST parse and render the JSON inline using the same recursive tree viewer.
- **FR-013**: Inline expanded content MUST respect the indentation level of its parent key.
- **FR-014**: Detected JSON blobs MUST default to the parsed tree view (JSON toggle active) on initial render.

**Smart Blob Detection - Markdown**
- **FR-015**: System MUST detect string values that likely contain Markdown (presence of common patterns: `**`, `*`, `#`, `-` lists, numbered lists, code blocks).
- **FR-016**: System MUST display detected Markdown content with a truncated preview and `[RAW]` and `[MD]` toggle pills.
- **FR-017**: When user activates `[MD]` toggle, system MUST render the Markdown inline with proper formatting.
- **FR-018**: Detected Markdown blobs MUST default to the rendered Markdown view (MD toggle active) on initial render.

**RAW View**
- **FR-019**: System MUST provide a `[RAW]` toggle for all string values to view unprocessed content.
- **FR-020**: RAW view MUST preserve whitespace, newlines, and display the exact string content.

**Inline Expansion Behavior**
- **FR-021**: All smart blob expansions MUST occur inline, pushing subsequent tree content down rather than opening modals or side panels.
- **FR-022**: Format toggles MUST allow switching between views (e.g., RAW ↔ JSON, RAW ↔ MD) without losing position in the tree.

**Error Handling**
- **FR-023**: When JSON parsing fails for a detected blob, system MUST gracefully fall back to RAW view.
- **FR-024**: System MUST handle malformed or circular data structures without crashing.

### Key Entities

- **TreeNode**: Represents a single node in the data tree. Contains: key (string), value (primitive/object/array), depth level, expanded state, children (for nested objects/arrays).
- **SmartBlob**: Represents a string value with detected structured content. Contains: raw value, detected type (JSON/Markdown/plain), current view mode, parsed content (if applicable).
- **ExpansionState**: Tracks the expanded/collapsed state of all tree nodes globally. Supports bulk operations (expand all, collapse all).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can view complete nested execution traces (3+ levels deep) immediately upon render without any clicks.
- **SC-002**: Users can toggle between collapsed and expanded views of the entire tree with a single click each.
- **SC-003**: Stringified JSON content can be expanded and inspected inline within 2 seconds of clicking the toggle.
- **SC-004**: Markdown content renders with proper formatting (bold, lists, headers) within 1 second of toggle activation.
- **SC-005**: The vertical space occupied by a typical event with 10 top-level keys is reduced by at least 40% compared to the current accordion-based UI.
- **SC-006**: 90% of developers familiar with browser DevTools can navigate the tree structure without instruction.
- **SC-007**: Event rendering for datasets up to 1000 nodes completes within 500ms.

## Clarifications

### Session 2025-12-26

- Q: Which toggle view should be active by default for Smart Blobs? → A: Default matches detected type (JSON → parsed tree, Markdown → rendered MD)
- Q: How should migration/rollout be handled? → A: Full replacement - remove old UI entirely, new renderer is the only option

## Assumptions

- Markdown detection uses heuristic pattern matching; false positives are acceptable since users can switch to RAW view.
- JSON detection triggers on strings starting with `{` or `[` - other JSON primitives in strings (numbers, booleans) are not detected as JSON blobs.
- Performance targets assume modern browsers (Chrome, Firefox, Safari latest 2 versions).
- Thread line styling follows common DevTools conventions (thin, muted color, vertical lines with horizontal connectors).
- The feature replaces the existing event stream rendering logic entirely with no fallback or toggle to the old UI.
