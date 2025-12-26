# Component API Contracts: DevTools-Style Event Stream Renderer

**Branch**: `004-devtools-event-renderer` | **Date**: 2025-12-26

This document defines the public interfaces for new and modified components.

---

## New Components

### DevToolsTree

Renders JSON data as a compact, DevTools-style hierarchical tree.

```python
class DevToolsTree:
    """DevTools-style hierarchical JSON tree renderer.
    
    Renders JSON data with:
    - Monospace typography with syntax coloring
    - Thin vertical thread lines connecting parent-child nodes
    - All nodes expanded by default
    - Collapsible nodes with click-to-toggle behavior
    - Smart blob detection and inline expansion for strings
    """
    
    def __init__(
        self,
        data: Any,
        tree_id: str,
        expansion_state: TreeExpansionState | None = None,
        blob_view_state: BlobViewState | None = None,
    ) -> None:
        """
        Initialize the DevTools tree.
        
        Args:
            data: JSON-serializable data to display
            tree_id: Unique identifier for state tracking
            expansion_state: Optional expansion state manager (creates new if None)
            blob_view_state: Optional blob view state manager (creates new if None)
        """
        ...
    
    def render(self) -> None:
        """Render the tree component."""
        ...
```

**CSS Classes** (for styling/testing):
- `.devtools-tree` - Root container
- `.devtools-tree-node` - Each tree node row
- `.devtools-tree-key` - Key/property name
- `.devtools-tree-value` - Primitive value display
- `.devtools-tree-toggle` - Expand/collapse chevron
- `.devtools-tree-thread-line` - Vertical guide line
- `.devtools-tree-children` - Children container

---

### SmartBlobDetector

Utility for detecting structured content in strings.

```python
class SmartBlobDetector:
    """Detects JSON and Markdown content in string values."""
    
    @staticmethod
    def detect_type(value: str) -> BlobType:
        """
        Detect the type of structured content in a string.
        
        Args:
            value: String to analyze
            
        Returns:
            BlobType.JSON if valid JSON object/array
            BlobType.MARKDOWN if contains Markdown patterns
            BlobType.PLAIN otherwise
        """
        ...
    
    @staticmethod
    def try_parse_json(value: str) -> tuple[Any, str | None]:
        """
        Attempt to parse string as JSON.
        
        Args:
            value: String to parse
            
        Returns:
            Tuple of (parsed_data, error_message)
            If successful: (data, None)
            If failed: (None, error_message)
        """
        ...
    
    @staticmethod
    def detect_markdown_patterns(value: str) -> bool:
        """
        Check if string contains Markdown patterns.
        
        Detects: headers (##), bold (**), lists (- or 1.), code blocks (```)
        
        Args:
            value: String to analyze
            
        Returns:
            True if Markdown patterns detected
        """
        ...
```

---

### TreeExpansionState

Manages expand/collapse state for tree nodes.

```python
@dataclass
class TreeExpansionState:
    """Tracks expand/collapse state for DevTools tree nodes.
    
    Uses sparse storage: only stores explicit user overrides.
    Global mode allows bulk expand/collapse operations.
    """
    
    global_mode: GlobalMode = GlobalMode.DEFAULT
    node_overrides: dict[str, bool] = field(default_factory=dict)
    default_expanded: bool = True
    
    def is_expanded(self, path: str) -> bool:
        """Get expansion state for a node path."""
        ...
    
    def toggle(self, path: str) -> None:
        """Toggle expansion state for a specific node."""
        ...
    
    def expand_all(self) -> None:
        """Expand all nodes (clears overrides, sets global mode)."""
        ...
    
    def collapse_all(self) -> None:
        """Collapse all nodes (clears overrides, sets global mode)."""
        ...
```

---

### BlobViewState

Manages view mode state for Smart Blobs.

```python
@dataclass
class BlobViewState:
    """Tracks view mode (RAW/JSON/MD) for smart blob elements.
    
    Defaults are determined by detected type:
    - JSON blobs default to JSON view
    - Markdown blobs default to MARKDOWN view
    - Plain strings default to RAW view
    """
    
    modes: dict[str, ViewMode] = field(default_factory=dict)
    
    def get_mode(self, path: str, detected_type: BlobType) -> ViewMode:
        """Get current view mode for a blob, using detection-based default."""
        ...
    
    def set_mode(self, path: str, mode: ViewMode) -> None:
        """Set view mode for a blob."""
        ...
```

---

### SmartBlobRenderer

Renders a string value with format toggles.

```python
class SmartBlobRenderer:
    """Renders string values with RAW/JSON/MD toggle pills.
    
    Provides inline expansion of structured content:
    - RAW: Monospace text with preserved whitespace
    - JSON: Recursive DevToolsTree rendering
    - MARKDOWN: Rendered Markdown via ui.markdown()
    """
    
    def __init__(
        self,
        value: str,
        path: str,
        depth: int,
        detected_type: BlobType,
        blob_view_state: BlobViewState,
        expansion_state: TreeExpansionState,
    ) -> None:
        """
        Initialize the smart blob renderer.
        
        Args:
            value: Raw string content
            path: Node path for state tracking
            depth: Current tree depth (for indentation)
            detected_type: Auto-detected content type
            blob_view_state: State manager for view modes
            expansion_state: State manager for nested tree expansion
        """
        ...
    
    def render(self) -> None:
        """Render the blob with toggle pills and content."""
        ...
```

**CSS Classes**:
- `.smart-blob-toggles` - Toggle pill container
- `.smart-blob-toggle` - Individual toggle pill
- `.smart-blob-toggle--active` - Active toggle state
- `.smart-blob-content` - Expanded content container

---

## Modified Components

### EventStream (existing)

Add global Expand All / Collapse All controls.

```python
# Changes to EventStream class:

class EventStream:
    def __init__(
        self,
        history: list[HistoryEntry],
        is_loading: bool = False,
        loading_tool: str | None = None,
    ) -> None:
        ...
        # NEW: Global expansion state shared across all event blocks
        self._global_expansion_state = TreeExpansionState(default_expanded=True)
    
    def _render_header(self) -> None:
        """Render stream header with global controls."""
        # ... existing code ...
        
        # NEW: Global expand/collapse buttons
        ui.button(icon="unfold_more", on_click=self._expand_all)
        ui.button(icon="unfold_less", on_click=self._collapse_all)
    
    def _expand_all(self) -> None:
        """Expand all tree nodes across all events."""
        self._global_expansion_state.expand_all()
        self._refresh_events()
    
    def _collapse_all(self) -> None:
        """Collapse all tree nodes across all events."""
        self._global_expansion_state.collapse_all()
        self._refresh_events()
```

---

### EventBlock (existing)

Replace JsonTree usage with DevToolsTree.

```python
# Changes to EventBlock subclasses:

class ToolOutputBlock(EventBlock):
    def render_content(self) -> None:
        # BEFORE:
        # render_json_tree(self.entry.result, ...)
        
        # AFTER:
        tree = DevToolsTree(
            data=self.entry.result,
            tree_id=f"{self.event_id}_result",
            expansion_state=self.state_manager.tree_expansion_state,
            blob_view_state=self.state_manager.blob_view_state,
        )
        tree.render()
```

---

## Style Constants

New additions to `styles.py`:

```python
# DevTools tree styling
DEVTOOLS_TREE_STYLES = {
    "font_family": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
    "font_size": "13px",
    "line_height": "1.4",
    "indent_size": "20px",
    "thread_line_color": "#E0E0E0",
    "key_color": "#881391",      # Purple for keys
    "string_color": "#C41A16",   # Red for strings
    "number_color": "#1C00CF",   # Blue for numbers
    "boolean_color": "#0D47A1",  # Dark blue for booleans
    "null_color": "#808080",     # Gray for null
    "bracket_color": "#000000",  # Black for brackets
}

SMART_BLOB_STYLES = {
    "toggle_bg": "#F5F5F5",
    "toggle_bg_active": "#1976D2",
    "toggle_text": "#616161",
    "toggle_text_active": "#FFFFFF",
    "toggle_border_radius": "4px",
    "toggle_padding": "2px 8px",
    "toggle_font_size": "11px",
}
```
