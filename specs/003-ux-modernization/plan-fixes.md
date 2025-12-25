# Implementation Plan: UX Modernization Event Stream Fixes

**Branch**: `003-ux-modernization-fixes` | **Date**: 2025-12-25 | **Spec**: [spec.md](spec.md)
**Input**: Gap analysis of User Story 2 acceptance scenarios from `/specs/003-ux-modernization/spec.md`

**Note**: This is a follow-up plan to address gaps identified after merging the initial 003-ux-modernization implementation.

## Summary

Three acceptance scenarios from User Story 2 (Structured Event Stream Interface) were not fully implemented:

1. **Expanded by default** (Scenario 4): Tool outputs and collapsible sections should be expanded when first rendered, but they default to collapsed
2. **State persistence** (Scenarios 5-6): Expand/collapse state is reset when UI actions occur or new events are added
3. **Bulk expand/collapse** (Scenarios 7-9): The buttons exist but do not function correctly

This plan addresses these gaps through proper test coverage and targeted fixes to the event stream state management.

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: NiceGUI (ui.expansion), Quasar (q-expansion-item)  
**Storage**: In-memory session state (no persistence across refresh per spec)  
**Testing**: pytest (unit), playwright (e2e)  
**Target Platform**: Linux/macOS/Windows desktop (browser-based UI)  
**Project Type**: Single Python library with NiceGUI UI layer  
**Performance Goals**: N/A (UX fix, no performance requirements)  
**Constraints**: Must not break existing functionality; session-only state (not persisted)  
**Scale/Scope**: ~3 component files affected, ~5 new test cases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Library-First Architecture | ✅ PASS | UI fixes remain within library boundary |
| II. Wrapper Integration Pattern | ✅ PASS | No changes to agent wrapping |
| III. Wizard of Oz Interaction Model | ✅ PASS | Enhances wizard inspection capabilities |
| IV. ADK Dependency & Abstractions | ✅ PASS | No ADK changes |
| V. Golden Trace Output | ✅ PASS | No trace format changes |
| VI. Hermetic Development Environment | ✅ PASS | Dev container unchanged |
| VII. Strict Development Standards | ✅ PASS | Will pass ruff/pyright/pytest |
| VIII. Flexible UI Strategy | ✅ PASS | Staying with NiceGUI |
| IX. Screenshot-Verified UX Changes | ⚠️ REQUIRED | Must capture updated screenshots |

**Gate Status**: PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-ux-modernization/
├── plan.md              # Original implementation plan
├── plan-fixes.md        # This file (fixes plan)
├── research.md          # Original research (reused)
├── data-model.md        # Original data model + additions
├── quickstart.md        # Original quickstart
├── contracts/           # Original contracts
└── tasks.md             # Original tasks
```

### Source Code (affected files)

```text
adk_agent_sim/
└── ui/
    └── components/
        ├── event_block.py      # Fix: expanded=True default, bulk buttons
        ├── event_stream.py     # Fix: state persistence across refresh
        └── json_tree.py        # Already correct (expanded=True)

tests/
├── unit/
│   └── test_event_block.py     # NEW: Unit tests for event block state
└── e2e/
    └── test_event_stream.py    # NEW: E2E tests for expand/collapse behavior
```

**Structure Decision**: Existing single-project structure. Fixes are isolated to UI components.

## Complexity Tracking

> No constitution violations. Fixes are minimal and targeted.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research (Gap Analysis)

### Root Cause Analysis

#### Issue 1: Sections Not Expanded by Default

**Current Code** ([event_stream.py#L65](../../adk_agent_sim/ui/components/event_stream.py#L65)):
```python
render_event_block(entry, expanded=False)  # Always passes False
```

**Problem**: The `render_event_block` function is called with `expanded=False` hardcoded, ignoring the spec requirement for expanded-by-default.

**Fix**: Change to `expanded=True` in both `EventStream._render_events()` and `RefreshableEventStream._render_stream()`.

---

#### Issue 2: State Not Persisted Across UI Actions

**Current Code** ([event_stream.py#L96-105](../../adk_agent_sim/ui/components/event_stream.py#L96)):
```python
def refresh(self, history, is_loading, loading_tool):
    if self._container:
        self._container.clear()  # Clears all DOM, losing expansion state
        with self._container:
            self._render_events()  # Re-renders from scratch
```

**Problem**: When the event stream refreshes (after tool execution, new events, etc.), the entire container is cleared and re-rendered. This destroys the DOM elements that hold expansion state.

**Fix**: Implement a state manager that:
1. Tracks expand/collapse state per event (keyed by event ID or index)
2. Preserves state during refresh by only adding new events, not clearing all
3. Or: Store state externally and restore during re-render

---

#### Issue 3: Expand All / Collapse All Buttons Non-functional

**Current Code** ([event_block.py#L48-68](../../adk_agent_sim/ui/components/event_block.py#L48)):
```python
def _expand_all(self) -> None:
    if self._card:
        ui.run_javascript(f'''
        document.querySelectorAll(
            '[id="{self._card.id}"] .q-expansion-item:not(.q-expansion-item--expanded)'
        ).forEach(el => el.querySelector('.q-item')?.click());
        ''')
```

**Problem**: The JavaScript selector `[id="{self._card.id}"]` may not match because NiceGUI generates IDs differently. The `ui.card()` element may not have an `id` attribute by default, or the ID format differs from what's expected.

**Fix**: 
1. Explicitly assign an ID to the card: `self._card = ui.card().props(f'id="event-{unique_id}"')`
2. Or use a different approach: Track expansion items in Python and call their `.set_value()` method directly

---

### Research Decision Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Use Python state dict for expansion tracking | Simpler than DOM inspection; works with NiceGUI refresh pattern | DOM-based state (rejected: lost on clear), Browser localStorage (rejected: spec says session-only) |
| Pass `expanded=True` as default | Direct fix for spec requirement | Add config option (rejected: over-engineering) |
| Use NiceGUI expansion `.set_value()` for bulk toggle | More reliable than JavaScript click simulation | Keep JS approach with fixed selectors (rejected: fragile) |
| Incremental event append instead of full clear | Preserves DOM state naturally | External state restore after clear (viable but more complex) |

---

## Phase 1: Design

### Data Model Additions

Add to [data-model.md](data-model.md):

```python
@dataclass
class EventExpansionState:
    """Tracks expand/collapse state for a single event block."""
    event_id: str  # Unique identifier (e.g., timestamp + type hash)
    sections: dict[str, bool]  # section_name -> is_expanded
    # Example: {"Arguments": True, "Result": False}

class ExpansionStateManager:
    """Manages expansion state across all events in a session."""
    
    def __init__(self) -> None:
        self._states: dict[str, EventExpansionState] = {}
        self._default_expanded: bool = True  # Per spec: expanded by default
    
    def get_state(self, event_id: str, section: str) -> bool:
        """Get expansion state for a section. Returns default if not tracked."""
        if event_id in self._states:
            return self._states[event_id].sections.get(section, self._default_expanded)
        return self._default_expanded
    
    def set_state(self, event_id: str, section: str, expanded: bool) -> None:
        """Update expansion state for a section."""
        if event_id not in self._states:
            self._states[event_id] = EventExpansionState(event_id, {})
        self._states[event_id].sections[section] = expanded
    
    def expand_all(self, event_id: str, sections: list[str]) -> None:
        """Expand all sections for an event."""
        for section in sections:
            self.set_state(event_id, section, True)
    
    def collapse_all(self, event_id: str, sections: list[str]) -> None:
        """Collapse all sections for an event."""
        for section in sections:
            self.set_state(event_id, section, False)
```

### Implementation Approach

#### Step 1: Create ExpansionStateManager

Location: `adk_agent_sim/ui/components/expansion_state.py` (new file)

```python
"""Expansion state management for event stream components."""

from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ExpansionStateManager:
    """Manages expand/collapse state for event blocks within a session."""
    
    _states: dict[str, dict[str, bool]] = field(default_factory=dict)
    default_expanded: bool = True
    
    def get(self, event_id: str, section: str) -> bool:
        """Get state, defaulting to default_expanded."""
        return self._states.get(event_id, {}).get(section, self.default_expanded)
    
    def set(self, event_id: str, section: str, expanded: bool) -> None:
        """Set expansion state."""
        if event_id not in self._states:
            self._states[event_id] = {}
        self._states[event_id][section] = expanded
    
    def expand_all(self, event_id: str) -> None:
        """Expand all tracked sections for an event."""
        if event_id in self._states:
            for section in self._states[event_id]:
                self._states[event_id][section] = True
    
    def collapse_all(self, event_id: str) -> None:
        """Collapse all tracked sections for an event."""
        if event_id in self._states:
            for section in self._states[event_id]:
                self._states[event_id][section] = False
```

#### Step 2: Update EventBlock to Use State Manager

Location: `adk_agent_sim/ui/components/event_block.py`

Changes:
1. Accept `state_manager` and `event_id` parameters
2. Use state manager to determine initial expansion state
3. Register callbacks when expansion state changes
4. Implement working expand_all/collapse_all using expansion references

#### Step 3: Update EventStream to Maintain State

Location: `adk_agent_sim/ui/components/event_stream.py`

Changes:
1. Create `ExpansionStateManager` instance on init
2. Pass state manager to each event block
3. Generate stable event IDs from history entries
4. Change from full-clear to incremental append where possible

#### Step 4: Fix Default Expansion

Location: `adk_agent_sim/ui/components/event_stream.py`

Change `expanded=False` to `expanded=True` in render calls.

---

## Test Plan

### Unit Tests: `tests/unit/test_event_block.py` (NEW)

```python
"""Unit tests for event block expansion state management."""

import pytest
from adk_agent_sim.ui.components.expansion_state import ExpansionStateManager


class TestExpansionStateManager:
    """Tests for ExpansionStateManager."""

    def test_default_state_is_expanded(self) -> None:
        """Verify default state matches spec requirement (expanded)."""
        manager = ExpansionStateManager()
        assert manager.get("event-1", "Arguments") is True
        assert manager.get("event-1", "Result") is True

    def test_set_and_get_state(self) -> None:
        """Verify state can be set and retrieved."""
        manager = ExpansionStateManager()
        manager.set("event-1", "Arguments", False)
        assert manager.get("event-1", "Arguments") is False
        assert manager.get("event-1", "Result") is True  # Unset = default

    def test_expand_all(self) -> None:
        """Verify expand_all expands all tracked sections."""
        manager = ExpansionStateManager()
        manager.set("event-1", "Arguments", False)
        manager.set("event-1", "Result", False)
        manager.expand_all("event-1")
        assert manager.get("event-1", "Arguments") is True
        assert manager.get("event-1", "Result") is True

    def test_collapse_all(self) -> None:
        """Verify collapse_all collapses all tracked sections."""
        manager = ExpansionStateManager()
        manager.set("event-1", "Arguments", True)
        manager.set("event-1", "Result", True)
        manager.collapse_all("event-1")
        assert manager.get("event-1", "Arguments") is False
        assert manager.get("event-1", "Result") is False

    def test_independent_events(self) -> None:
        """Verify different events have independent state."""
        manager = ExpansionStateManager()
        manager.set("event-1", "Arguments", False)
        manager.set("event-2", "Arguments", True)
        assert manager.get("event-1", "Arguments") is False
        assert manager.get("event-2", "Arguments") is True
```

### E2E Tests: `tests/e2e/test_event_stream.py` (NEW)

```python
"""E2E tests for event stream expand/collapse behavior."""

from playwright.sync_api import Page, expect

ELEMENT_TIMEOUT = 10000


class TestEventStreamExpansion:
    """Tests for User Story 2 acceptance scenarios 4-9."""

    def test_tool_output_expanded_by_default(self, page: Page) -> None:
        """Scenario 4: Tool outputs expanded by default.
        
        Given a tool call or tool output event,
        When it first renders,
        Then all collapsible sections are expanded by default.
        """
        # Setup: Start session and execute a tool
        # ... navigation to execute tool ...
        
        # Verify: Check that expansion items have expanded class
        expansion = page.locator(".q-expansion-item--expanded")
        expect(expansion.first).to_be_visible(timeout=ELEMENT_TIMEOUT)

    def test_collapse_state_preserved_on_action(self, page: Page) -> None:
        """Scenario 5: Collapse state preserved during UI actions.
        
        Given a user has collapsed a section in an event,
        When they perform another UI action,
        Then the collapsed state is preserved.
        """
        # Setup: Execute tool, collapse a section
        # ... navigation ...
        
        # Collapse a section
        page.locator(".q-expansion-item--expanded .q-item").first.click()
        
        # Perform UI action (e.g., select another tool)
        # ... action ...
        
        # Verify: Section still collapsed
        collapsed = page.locator(".q-expansion-item:not(.q-expansion-item--expanded)")
        expect(collapsed.first).to_be_visible()

    def test_expand_state_preserved_on_new_event(self, page: Page) -> None:
        """Scenario 6: Expand state preserved when new events added.
        
        Given a user has expanded a section in an event,
        When new events are added to the stream,
        Then the expanded state of existing events is preserved.
        """
        # Similar to above but trigger new event addition
        pass

    def test_expand_all_button_works(self, page: Page) -> None:
        """Scenario 8: Expand All button expands all sections.
        
        Given an event block with some sections collapsed,
        When the user clicks "Expand All",
        Then all collapsible children within that event expand.
        """
        # Find and click Expand All button
        page.locator("button[aria-label='Expand All']").first.click()
        
        # Verify all sections expanded
        # ... assertions ...

    def test_collapse_all_button_works(self, page: Page) -> None:
        """Scenario 9: Collapse All button collapses all sections.
        
        Given an event block with some sections expanded,
        When the user clicks "Collapse All",
        Then all collapsible children within that event collapse.
        """
        # Find and click Collapse All button
        page.locator("button[aria-label='Collapse All']").first.click()
        
        # Verify all sections collapsed
        # ... assertions ...
```

---

## Implementation Sequence

1. **Create `expansion_state.py`** with `ExpansionStateManager` class
2. **Add unit tests** for `ExpansionStateManager`
3. **Update `event_stream.py`** to pass `expanded=True` (quick fix)
4. **Update `event_block.py`** to accept and use state manager
5. **Update `event_stream.py`** to create and pass state manager
6. **Fix expand/collapse all buttons** with proper element references
7. **Add E2E tests** for acceptance scenarios
8. **Capture screenshots** for verification

---

## Acceptance Criteria Mapping

| Scenario | Spec Requirement | Implementation | Test |
|----------|-----------------|----------------|------|
| 4 | Expanded by default | `expanded=True` in render_event_block | `test_tool_output_expanded_by_default` |
| 5 | State preserved on action | ExpansionStateManager | `test_collapse_state_preserved_on_action` |
| 6 | State preserved on new events | Incremental append + state manager | `test_expand_state_preserved_on_new_event` |
| 7 | Expand/Collapse All visible | Already implemented (buttons exist) | Visual verification |
| 8 | Expand All works | Fix button handler with expansion refs | `test_expand_all_button_works` |
| 9 | Collapse All works | Fix button handler with expansion refs | `test_collapse_all_button_works` |
