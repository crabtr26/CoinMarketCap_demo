import os
import sys
from pathlib import Path

from typer.testing import CliRunner

sys.path.append(str(Path(__file__).parent.parent))
from src.cli import app

runner = CliRunner()


def test_detect():
    mock_data_path = os.path.join(
        str(Path(__file__).parent), "mock_data/test_cases.json"
    )
    result = runner.invoke(app, ["detect", mock_data_path])
    assert result.exit_code == 0
    assert "Transactions" in result.stdout
    assert "Transfers" in result.stdout
