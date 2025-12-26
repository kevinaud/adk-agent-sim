# Research: DevTools-Style Event Stream Renderer

**Branch**: `004-devtools-event-renderer` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)

## Research Tasks

### Task 1: NiceGUI Tree Rendering Patterns

**Question**: How should we implement a DevTools-style tree with thread lines in NiceGUI?

**Findings**:
- NiceGUI provides `ui.expansion()` for collapsible content but it uses Material Design styling (heavy borders, icons)
- Native CSS approach needed for thread lines (using `::before` pseudo-elements with `border-left`)
- The existing `JsonTree` component uses `ui.expansion()` which is too heavy for the DevTools aesthetic
- Best approach: Custom component using `ui.column()` with CSS for thread lines and click handlers for expand/collapse

**Decision**: Create a new `DevToolsTree` component that renders JSON as a lightweight tree with:
- Custom CSS for monospace text, syntax coloring, and thread lines
- Manual expand/collapse state management (not relying on `ui.expansion()`)
- Recursive rendering with depth tracking for indentation
- **CRITICAL**: Build entirely from scratch — do NOT reuse any code from existing `json_tree.py`

**Alternatives Considered**:
1. Modify existing `JsonTree` - Rejected: Existing implementation has multiple hard-to-diagnose bugs; too coupled to `ui.expansion()` Material Design
2. Reuse parsing/rendering logic from `json_tree.py` - Rejected: Bugs in existing code make it unreliable; clean-room implementation preferred
3. Use third-party tree library - Rejected: NiceGUI ecosystem doesn't have a DevTools-style tree

---

### Task 2: Smart Blob Content Detection

**Question**: How should we detect and parse embedded JSON/Markdown in string values?

**Findings**:
- Existing `text_presenter.py` has `_try_parse_as_data()` for JSON detection (handles `json.loads` and `ast.literal_eval`)
- Markdown detection needs heuristics: patterns like `**`, `##`, `- `, `1. `, triple backticks
- Detection should happen at render time, not parse time (lazy evaluation)

**Decision**: Create `SmartBlobDetector` utility class with:
- `detect_json(s: str) -> tuple[Any, bool]` - reuse existing parsing logic
- `detect_markdown(s: str) -> bool` - regex-based heuristics
- `detect_type(s: str) -> Literal["json", "markdown", "plain"]`

**Alternatives Considered**:
1. Eager detection in data model - Rejected: Adds latency for large datasets
2. Use markdown parsing library for detection - Rejected: Overkill for heuristic detection

---

### Task 3: Expansion State Management for Tree Nodes

**Question**: How do we manage expand/collapse state for potentially thousands of tree nodes?

**Findings**:
- Existing `ExpansionStateManager` tracks state by event_id + section name
- New approach needs path-based addressing (e.g., `"root.execution_trace.0.console_log"`)
- "Expand All" / "Collapse All" must be performant (O(1) via flag, not O(n) updates)

**Decision**: Extend state management with:
- Path-based node identification
- Global expand/collapse override flag
- Per-node state only stored when user explicitly toggles (sparse storage)

**Alternatives Considered**:
1. Store full state for all nodes - Rejected: Memory overhead for large datasets
2. Stateless (re-render everything) - Rejected: Loses user's expand/collapse choices

---

### Task 4: Thread Line CSS Implementation

**Question**: What CSS pattern creates DevTools-style thread lines?

**Findings**:
- Chrome DevTools uses `::before` pseudo-element with `border-left`
- Line must span from toggle chevron to bottom of children block
- Need to handle last-child differently (no continuing line below)
- Indentation: ~16-20px per level

**Decision**: CSS pattern:
```css
.tree-node {
  position: relative;
  padding-left: 20px;
}
.tree-node::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  border-left: 1px solid #ddd;
}
.tree-node:last-child::before {
  height: 12px; /* Only goes to chevron, not full height */
}
```

**Alternatives Considered**:
1. SVG lines - Rejected: More complex, no visual benefit
2. Background images - Rejected: Harder to maintain and theme

---

### Task 5: Toggle Pill UI Pattern

**Question**: How should format toggle pills (`[RAW]`, `[JSON]`, `[MD]`) be styled and behave?

**Findings**:
- Current `TextPresenter` uses full buttons - too large/heavy
- DevTools uses small, pill-shaped toggles with muted colors
- Active toggle should be visually distinct (solid background vs outline)

**Decision**: Implement as `ui.button()` with custom props:
- Size: `size=xs` with custom padding
- Style: outlined when inactive, solid primary when active
- Layout: horizontal row, tight gap (4px)

**Alternatives Considered**:
1. Radio buttons - Rejected: Not visually consistent with DevTools aesthetic
2. Tabs - Rejected: Too heavy for inline use

---

### Task 6: Performance for Large Datasets

**Question**: How do we ensure <500ms render for 1000 nodes (SC-007)?

**Findings**:
- NiceGUI renders server-side, sends HTML over WebSocket
- 1000 nodes = ~1000 HTML elements minimum
- Virtualization complex in NiceGUI (no native support)
- Initial render can be lazy (expand on demand vs. render all)

**Decision**: Two-phase approach:
1. **Phase 1 (MVP)**: Render all visible nodes, trust browser for DOM performance
2. **Future optimization**: If performance issues arise, implement "render on expand" for deeply nested content

**Alternatives Considered**:
1. Full virtualization - Rejected: Too complex for MVP, may not be needed
2. Pagination - Rejected: Breaks the "see everything at once" requirement

---

## Summary

## Critical Constraints

> ⚠️ **NO CODE REUSE**: The existing `json_tree.py` implementation has multiple bugs that have been difficult to diagnose. The new `DevToolsTree` component MUST be implemented from scratch without reusing any code from `json_tree.py`. This is a clean-room implementation.

## Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Tree component | New `DevToolsTree` with custom CSS | `ui.expansion()` too heavy |
| Smart blob detection | `SmartBlobDetector` utility | Lazy detection, reuse existing JSON parser |
| State management | Path-based sparse storage | Memory efficient for large datasets |
| Thread lines | CSS `::before` pseudo-elements | Standard pattern, easy to theme |
| Toggle pills | Small `ui.button()` with custom styling | Compact, accessible |
| Performance | Render all, optimize later | Simplest approach, test against targets |
