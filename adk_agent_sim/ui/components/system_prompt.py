"""Collapsible system prompt/instructions component."""

from nicegui import ui

from adk_agent_sim.ui.styles import EXPANDABLE_HEADER_CLASSES


class SystemPromptHeader:
  """Expandable header component for displaying agent system instructions."""

  def __init__(
    self,
    content: str,
    agent_name: str,
    expanded: bool = False,
  ) -> None:
    """
    Initialize the system prompt header.

    Args:
      content: The agent's system instruction text
      agent_name: Name of the agent
      expanded: Initial expansion state (default: collapsed)
    """
    self.content = content
    self.agent_name = agent_name
    self.expanded = expanded

  def render(self) -> None:
    """Render the expandable system prompt header."""
    with ui.expansion(
      "System Instructions",
      icon="psychology",
      value=self.expanded,  # Collapsed by default
    ).classes(EXPANDABLE_HEADER_CLASSES):
      # Header info
      with ui.row().classes("items-center gap-2 mb-2"):
        ui.badge(self.agent_name, color="blue")
        ui.label("•").classes("text-gray-400")
        word_count = len(self.content.split()) if self.content else 0
        ui.label(f"{word_count} words").classes("text-xs text-gray-500")

      # Content
      if self.content:
        with ui.scroll_area().classes("max-h-64"):
          ui.markdown(self.content).classes("text-sm")
      else:
        ui.label("No system instructions defined").classes(
          "text-gray-500 italic text-sm"
        )


# Keep the old class for backwards compatibility
class SystemPromptPanel(SystemPromptHeader):
  """Legacy alias for SystemPromptHeader."""

  def __init__(self, instruction: str, agent_name: str) -> None:
    """Initialize with legacy signature (expanded by default for compatibility)."""
    super().__init__(content=instruction, agent_name=agent_name, expanded=True)


def render_system_prompt(
  instruction: str,
  agent_name: str,
  expanded: bool = False,
) -> SystemPromptHeader:
  """
  Render a system prompt header.

  Args:
    instruction: System instruction text
    agent_name: Agent name
    expanded: Initial expansion state (default: collapsed)

  Returns:
    SystemPromptHeader instance
  """
  header = SystemPromptHeader(instruction, agent_name, expanded)
  header.render()
  return header
