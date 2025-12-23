from unittest.mock import patch

from typer.testing import CliRunner

from adk_agent_sim.demo.demo import app

runner = CliRunner()


def test_hello():
  with patch("adk_agent_sim.simulator.AgentSimulator.run") as mock_run:
    result = runner.invoke(app, ["--port", "9000"])
    assert result.exit_code == 0
    assert "9000" in result.stdout
    mock_run.assert_called_once()
