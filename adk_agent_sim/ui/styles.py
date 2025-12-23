"""Shared CSS constants and styles for the UI."""

# Color palette
COLORS = {
  "primary": "#1976D2",
  "secondary": "#424242",
  "accent": "#82B1FF",
  "error": "#FF5252",
  "warning": "#FFC107",
  "success": "#4CAF50",
  "info": "#2196F3",
  "background": "#FAFAFA",
  "surface": "#FFFFFF",
  "text_primary": "#212121",
  "text_secondary": "#757575",
}

# History entry colors
HISTORY_COLORS = {
  "user_query": "#E3F2FD",  # Light blue
  "tool_call": "#FFF3E0",  # Light orange
  "tool_output": "#E8F5E9",  # Light green
  "tool_error": "#FFEBEE",  # Light red
  "final_response": "#F3E5F5",  # Light purple
}

# History entry border colors
HISTORY_BORDER_COLORS = {
  "user_query": "#1976D2",  # Blue
  "tool_call": "#F57C00",  # Orange
  "tool_output": "#388E3C",  # Green
  "tool_error": "#D32F2F",  # Red
  "final_response": "#7B1FA2",  # Purple
}

# Card styles
CARD_STYLE = """
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 12px;
"""

# History entry base style
HISTORY_ENTRY_STYLE = """
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-left: 4px solid;
"""

# Panel styles
PANEL_HEADER_STYLE = """
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #212121;
"""

# Form field styles
FIELD_STYLE = """
  margin-bottom: 8px;
"""

# Button styles
PRIMARY_BUTTON_STYLE = """
  background-color: #1976D2;
  color: white;
"""

DANGER_BUTTON_STYLE = """
  background-color: #D32F2F;
  color: white;
"""

SUCCESS_BUTTON_STYLE = """
  background-color: #388E3C;
  color: white;
"""

# Timer styles
TIMER_STYLE = """
  font-family: monospace;
  font-size: 1.2rem;
  color: #757575;
"""

# Layout constants
SIDEBAR_WIDTH = 300
MAIN_CONTENT_MIN_WIDTH = 600
HISTORY_PANEL_HEIGHT = "calc(100vh - 300px)"
