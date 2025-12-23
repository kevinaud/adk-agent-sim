"""Collapsible system prompt/instructions component."""

from __future__ import annotations

from nicegui import ui


class SystemPromptPanel:
  """Component for displaying agent system instructions."""

  def __init__(self, instruction: str, agent_name: str) -> None:
    """
    Initialize the system prompt panel.

    Args:
      instruction: The agent's system instruction text
      agent_name: Name of the agent
    """
    self.instruction = instruction
    self.agent_name = agent_name

  def render(self) -> None:
    """Render the system prompt panel."""
    with ui.expansion(
      f"System Instructions ({self.agent_name})",
      icon="psychology",
      value=True,  # Expanded by default
    ).classes("w-full mb-4"):
      if self.instruction:
        ui.markdown(self.instruction).classes("text-sm")
      else:
        ui.label("No system instructions defined").classes("text-gray-500 italic")


def render_system_prompt(instruction: str, agent_name: str) -> SystemPromptPanel:
  """
  Render a system prompt panel.

  Args:
    instruction: System instruction text
    agent_name: Agent name

  Returns:
    SystemPromptPanel instance
  """
  panel = SystemPromptPanel(instruction, agent_name)
  panel.render()
  return panel
