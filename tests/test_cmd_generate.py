#!/usr/bin/env python3
# CLI integration tests for the generate subcommand.
from __future__ import annotations

from click.testing import CliRunner

from soma_upgrade_prerequisites.main import cli


def test_generate_help() -> None:
    """generate --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 0
    assert "generate" in result.output.lower()


def test_generate_invalid_option() -> None:
    """Invalid options produce exit code 2."""
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--nonexistent"])
    assert result.exit_code == 2
