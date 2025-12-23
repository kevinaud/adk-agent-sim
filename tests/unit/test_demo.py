from typer.testing import CliRunner

from adk_agent_sim.demo.demo import app

runner = CliRunner()


def test_hello():
  result = runner.invoke(app, ["--port", "9000"])
  assert result.exit_code == 0
  assert "9000" in result.stdout
