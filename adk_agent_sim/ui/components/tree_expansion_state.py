"""Expansion state management for DevTools tree nodes.

This module provides state tracking for tree node expand/collapse behavior
using a simple dict mapping paths to expanded state.

Clean-room implementation: No code reused from json_tree.py.
"""

from dataclasses import dataclass, field


@dataclass
class TreeExpansionState:
  """Tracks expand/collapse state for DevTools tree nodes.

  Uses a dict to store expansion state for each path.
  Unknown paths return the default_expanded value.

  Attributes:
    node_states: Path -> expanded state mapping
    default_expanded: Default state for nodes not in node_states
  """

  node_states: dict[str, bool] = field(default_factory=dict)
  default_expanded: bool = True

  def is_expanded(self, path: str) -> bool:
    """Get expansion state for a node path.

    Args:
      path: Unique path identifier for the node (e.g., "root.items.0.name")

    Returns:
      True if the node should be expanded, False otherwise
    """
    return self.node_states.get(path, self.default_expanded)

  def toggle(self, path: str) -> None:
    """Toggle expansion state for a specific node.

    Args:
      path: Unique path identifier for the node
    """
    current_state = self.is_expanded(path)
    self.node_states[path] = not current_state

  def expand_all(self, paths: list[str]) -> None:
    """Expand all specified nodes.

    Args:
      paths: List of node paths to expand
    """
    for path in paths:
      self.node_states[path] = True

  def collapse_all(self, paths: list[str]) -> None:
    """Collapse all specified nodes.

    Args:
      paths: List of node paths to collapse
    """
    for path in paths:
      self.node_states[path] = False

  def reset(self) -> None:
    """Reset to default state.

    Clears all stored states. Nodes will use default_expanded value.
    """
    self.node_states.clear()
