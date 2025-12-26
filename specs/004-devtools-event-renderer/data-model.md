# Data Model: DevTools-Style Event Stream Renderer

**Branch**: `004-devtools-event-renderer` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)

## Overview

This feature is a **UI-only change** with no persistent data storage. All state is session-only (in-memory) and resets on page refresh.

## Entities

### TreeNode

Represents a single node in the hierarchical JSON tree.

```
TreeNode
├── path: str               # Unique path identifier (e.g., "root.trace.0.config")
├── key: str                # Display key (e.g., "config", "[0]", "status")
├── value: Any              # Raw value (primitive, dict, list)
├── value_type: ValueType   # Enum: OBJECT, ARRAY, STRING, NUMBER, BOOLEAN, NULL
├── depth: int              # Nesting level (0 = root)
├── children: list[TreeNode]  # Child nodes (empty for primitives)
└── smart_blob: SmartBlob | None  # Detected structured content (strings only)
```

**Notes**:
- `path` is computed at render time from parent path + key
- `children` are lazily populated during recursive rendering
- `smart_blob` is only set for string values that pass detection

---

### SmartBlob

Represents detected structured content within a string value.

```
SmartBlob
├── raw_value: str                # Original string content
├── detected_type: BlobType       # Enum: JSON, MARKDOWN, PLAIN
├── parsed_content: Any | None    # Parsed JSON (if JSON type), else None
└── parse_error: str | None       # Error message if parsing failed
```

**Detection Rules**:
| Type | Detection Criteria |
|------|-------------------|
| JSON | String starts with `{` or `[` AND `json.loads()` succeeds |
| MARKDOWN | String contains any of: `**`, `##`, `- ` (list), `1. ` (numbered), triple backticks |
| PLAIN | Neither JSON nor MARKDOWN detected |

---

### TreeExpansionState

Manages expand/collapse state for the entire tree.

```
TreeExpansionState
├── global_mode: GlobalMode       # Enum: DEFAULT, ALL_EXPANDED, ALL_COLLAPSED
├── node_overrides: dict[str, bool]  # path -> expanded (sparse storage)
└── default_expanded: bool        # True per spec requirement
```

**State Resolution Logic**:
```
is_expanded(path):
  if path in node_overrides:
    return node_overrides[path]
  if global_mode == ALL_EXPANDED:
    return True
  if global_mode == ALL_COLLAPSED:
    return False
  return default_expanded
```

**Operations**:
- `expand_all()`: Sets `global_mode = ALL_EXPANDED`, clears overrides
- `collapse_all()`: Sets `global_mode = ALL_COLLAPSED`, clears overrides
- `toggle(path)`: Adds override for specific path

---

### BlobViewState

Manages which view mode is active for each Smart Blob.

```
BlobViewState
├── modes: dict[str, ViewMode]    # path -> current mode
└── defaults: dict[str, ViewMode] # path -> auto-detected default
```

**ViewMode Enum**:
- `RAW`: Show raw string content
- `JSON`: Show parsed JSON tree
- `MARKDOWN`: Show rendered Markdown

**Default Mode Selection** (per clarification):
- JSON blobs default to `JSON` view
- Markdown blobs default to `MARKDOWN` view
- Plain strings default to `RAW` view

---

## Enums

```python
class ValueType(Enum):
  OBJECT = "object"
  ARRAY = "array"
  STRING = "string"
  NUMBER = "number"
  BOOLEAN = "boolean"
  NULL = "null"

class BlobType(Enum):
  JSON = "json"
  MARKDOWN = "markdown"
  PLAIN = "plain"

class ViewMode(Enum):
  RAW = "raw"
  JSON = "json"
  MARKDOWN = "markdown"

class GlobalMode(Enum):
  DEFAULT = "default"       # Use default_expanded for all nodes
  ALL_EXPANDED = "expanded" # Force all nodes expanded
  ALL_COLLAPSED = "collapsed" # Force all nodes collapsed
```

---

## State Lifecycle

```
Page Load
    │
    ▼
┌─────────────────────┐
│ TreeExpansionState  │◄──── global_mode = DEFAULT
│ (default_expanded   │       node_overrides = {}
│  = True)            │
└─────────────────────┘
    │
    ▼
User clicks node toggle
    │
    ▼
┌─────────────────────┐
│ node_overrides[path]│◄──── Add specific override
│ = !current          │
└─────────────────────┘
    │
    ▼
User clicks "Collapse All"
    │
    ▼
┌─────────────────────┐
│ global_mode =       │◄──── Clear all overrides
│ ALL_COLLAPSED       │       node_overrides = {}
└─────────────────────┘
    │
    ▼
Page Refresh
    │
    ▼
┌─────────────────────┐
│ All state reset     │◄──── No persistence
└─────────────────────┘
```

---

## Relationships

```
EventStream (existing)
    │
    ├── contains ──► EventBlock (existing, modified)
    │                    │
    │                    └── renders ──► DevToolsTree (NEW)
    │                                        │
    │                                        ├── uses ──► TreeExpansionState
    │                                        │
    │                                        └── contains ──► TreeNode[]
    │                                                            │
    │                                                            └── may have ──► SmartBlob
    │                                                                                │
    │                                                                                └── uses ──► BlobViewState
    │
    └── has ──► Global Controls (Expand All / Collapse All)
```

---

## Migration Notes

- **No database migration required** - all state is in-memory
- **Replaces**: Existing `JsonTree` component usage in `EventBlock`
- **Reuses**: `ExpansionStateManager` patterns (extend, don't replace)
- **Reuses**: `PresentationModeManager` for blob view state
