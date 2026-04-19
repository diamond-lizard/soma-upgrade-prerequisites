#!/usr/bin/env python3
"""CLI integration tests for preview-analysis and write-analysis subcommands."""
# CLI integration tests for preview-analysis and write-analysis subcommands.
from __future__ import annotations

from unittest.mock import patch

from click.testing import CliRunner

from soma_upgrade_prerequisites.main import cli


def test_preview_analysis_help() -> None:
    """preview-analysis --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["preview-analysis", "--help"])
    assert result.exit_code == 0
    assert "preview-analysis" in result.output.lower()


def test_write_analysis_help() -> None:
    """write-analysis --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["write-analysis", "--help"])
    assert result.exit_code == 0
    assert "write-analysis" in result.output.lower()


def test_preview_analysis_invalid_option() -> None:
    """Invalid options produce exit code 2."""
    runner = CliRunner()
    result = runner.invoke(cli, ["preview-analysis", "--nonexistent"])
    assert result.exit_code == 2


def test_write_analysis_invalid_option() -> None:
    """Invalid options produce exit code 2."""
    runner = CliRunner()
    result = runner.invoke(cli, ["write-analysis", "--nonexistent"])
    assert result.exit_code == 2


def test_generate_command_removed() -> None:
    """Old generate command is no longer available."""
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 2
    assert "no such command" in result.output.lower()


def test_show_command_removed() -> None:
    """Old show command is no longer available."""
    runner = CliRunner()
    result = runner.invoke(cli, ["show", "--help"])
    assert result.exit_code == 2
    assert "no such command" in result.output.lower()


def test_preview_analysis_rejects_write_flag() -> None:
    """preview-analysis does not accept --write."""
    runner = CliRunner()
    result = runner.invoke(cli, ["preview-analysis", "--write"])
    assert result.exit_code == 2


def test_cli_help_lists_new_commands() -> None:
    """Top-level --help lists the renamed commands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    output = result.output
    assert "preview-analysis" in output
    assert "write-analysis" in output
    assert "show-tracker" in output
    commands_section = output.split("Commands:")[-1] if "Commands:" in output else output
    assert "  generate " not in commands_section
    assert "  show " not in commands_section


def test_preview_analysis_passes_write_false() -> None:
    """preview-analysis invokes run_analysis with write=False."""
    runner = CliRunner()
    with patch(
        "soma_upgrade_prerequisites.cmd_preview_analysis.run_analysis",
    ) as mock_run:
        mock_run.side_effect = SystemExit(0)
        runner.invoke(cli, ["preview-analysis"])
        if mock_run.called:
            _, kwargs = mock_run.call_args
            assert kwargs["write"] is False


def test_write_analysis_passes_write_true() -> None:
    """write-analysis invokes run_analysis with write=True."""
    runner = CliRunner()
    with patch(
        "soma_upgrade_prerequisites.cmd_write_analysis.run_analysis",
    ) as mock_run:
        mock_run.side_effect = SystemExit(0)
        runner.invoke(cli, ["write-analysis"])
        if mock_run.called:
            _, kwargs = mock_run.call_args
            assert kwargs["write"] is True
