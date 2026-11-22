"""CLI testing with Typer CliRunner."""
import pytest
from typer.testing import CliRunner
from axiom.cli import app

runner = CliRunner()

def test_cli_status():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "AXIOM AI AGENTS" in result.output
    assert "Market Data Engine" in result.output

def test_cli_sources():
    result = runner.invoke(app, ["sources"])
    assert result.exit_code == 0
    assert "Yahoo Finance" in result.output
    assert "SEC EDGAR" in result.output

def test_cli_report_latest():
    result = runner.invoke(app, ["report", "latest"])
    assert result.exit_code == 0
    assert "Menampilkan Laporan Terbaru" in result.output
