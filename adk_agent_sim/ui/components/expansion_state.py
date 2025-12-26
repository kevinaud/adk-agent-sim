"""Expansion state management for event stream components.

This module provides the ExpansionStateManager class to track expand/collapse
state for event blocks within a simulation session. Per the UX spec, state
is session-only (in-memory) and NOT persisted across page refreshes.
"""

from dataclasses import dataclass, field


@dataclass
class ExpansionStateManager:
  """Manages expand/collapse state for event blocks within a session.

  This class tracks which sections (e.g., "Arguments", "Result") are expanded
  or collapsed for each event in the event stream. The default state is
  expanded (per spec requirement).

  Attributes:
    default_expanded: Default expansion state for untracked sections.
  """

  _states: dict[str, dict[str, bool]] = field(default_factory=dict)
  default_expanded: bool = True

  def get(self, event_id: str, section: str) -> bool:
    """Get expansion state for a section.

    Args:
      event_id: Unique identifier for the event block.
      section: Name of the section (e.g., "Arguments", "Result").

    Returns:
      True if expanded, False if collapsed. Returns default_expanded
      if the section has not been explicitly set.
    """
    return self._states.get(event_id, {}).get(section, self.default_expanded)

  def set(self, event_id: str, section: str, expanded: bool) -> None:
    """Set expansion state for a section.

    Args:
      event_id: Unique identifier for the event block.
      section: Name of the section (e.g., "Arguments", "Result").
      expanded: True to expand, False to collapse.
    """
    if event_id not in self._states:
      self._states[event_id] = {}
    self._states[event_id][section] = expanded

  def expand_all(self, event_id: str) -> None:
    """Expand all tracked sections for an event.

    Only affects sections that have been explicitly tracked via set().
    New/untracked sections will use default_expanded (True).

    Args:
      event_id: Unique identifier for the event block.
    """
    if event_id in self._states:
      for section in self._states[event_id]:
        self._states[event_id][section] = True

  def collapse_all(self, event_id: str) -> None:
    """Collapse all tracked sections for an event.

    Only affects sections that have been explicitly tracked via set().

    Args:
      event_id: Unique identifier for the event block.
    """
    if event_id in self._states:
      for section in self._states[event_id]:
        self._states[event_id][section] = False

  def get_sections(self, event_id: str) -> list[str]:
    """Get list of tracked sections for an event.

    Args:
      event_id: Unique identifier for the event block.

    Returns:
      List of section names that have been tracked for this event.
    """
    return list(self._states.get(event_id, {}).keys())

  def clear(self) -> None:
    """Clear all tracked state.

    Useful when starting a new session.
    """
    self._states.clear()
