"""Expansion state management for DevTools tree nodes.

This module provides state tracking for tree node expand/collapse behavior
using sparse storage - only explicit user overrides are stored.

Clean-room implementation: No code reused from json_tree.py.
"""

from dataclasses import dataclass, field
from enum import Enum


class GlobalMode(Enum):
  """Global expansion mode for bulk operations."""

  DEFAULT = "default"  # Use default_expanded for all nodes
  ALL_EXPANDED = "expanded"  # Force all nodes expanded
  ALL_COLLAPSED = "collapsed"  # Force all nodes collapsed


@dataclass
class TreeExpansionState:
  """Tracks expand/collapse state for DevTools tree nodes.

  Uses sparse storage: only stores explicit user overrides.
  Global mode allows bulk expand/collapse operations.

  Attributes:
    global_mode: Current global expansion mode
    node_overrides: Path -> expanded state (sparse storage)
    default_expanded: Default state for nodes without overrides
  """

  global_mode: GlobalMode = GlobalMode.DEFAULT
  node_overrides: dict[str, bool] = field(default_factory=dict)
  default_expanded: bool = True

  def is_expanded(self, path: str) -> bool:
    """Get expansion state for a node path.

    Resolution order:
    1. Check node_overrides for explicit user choice
    2. Check global_mode for bulk operations
    3. Fall back to default_expanded

    Args:
      path: Unique path identifier for the node (e.g., "root.items.0.name")

    Returns:
      True if the node should be expanded, False otherwise
    """
    # Priority 1: Explicit user override
    if path in self.node_overrides:
      return self.node_overrides[path]

    # Priority 2: Global mode
    if self.global_mode == GlobalMode.ALL_EXPANDED:
      return True
    if self.global_mode == GlobalMode.ALL_COLLAPSED:
      return False

    # Priority 3: Default
    return self.default_expanded

  def toggle(self, path: str) -> None:
    """Toggle expansion state for a specific node.

    This creates an explicit override for the node path.
    The current effective state is inverted.

    Args:
      path: Unique path identifier for the node
    """
    current_state = self.is_expanded(path)
    self.node_overrides[path] = not current_state

  def expand_all(self) -> None:
    """Expand all nodes.

    Sets global mode to ALL_EXPANDED and clears all overrides.
    This is O(1) regardless of tree size.
    """
    self.global_mode = GlobalMode.ALL_EXPANDED
    self.node_overrides.clear()

  def collapse_all(self) -> None:
    """Collapse all nodes.

    Sets global mode to ALL_COLLAPSED and clears all overrides.
    This is O(1) regardless of tree size.
    """
    self.global_mode = GlobalMode.ALL_COLLAPSED
    self.node_overrides.clear()

  def reset(self) -> None:
    """Reset to default state.

    Sets global mode to DEFAULT and clears all overrides.
    Nodes will use default_expanded value.
    """
    self.global_mode = GlobalMode.DEFAULT
    self.node_overrides.clear()
