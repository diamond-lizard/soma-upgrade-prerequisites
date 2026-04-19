#!/usr/bin/env python3
"""CLI entry point for soma-upgrade-prerequisites."""
# CLI entry point for soma-upgrade-prerequisites.
# Defines the click group and registers subcommands.
from __future__ import annotations

import importlib.metadata

import click

from .cmd_preview_analysis import preview_analysis
from .cmd_show_tracker import show_tracker
from .cmd_update_note import update_note
from .cmd_update_status import update_status
from .cmd_validate import validate
from .cmd_write_analysis import write_analysis


@click.group(context_settings={"max_content_width": 9999})
@click.version_option(
    version=importlib.metadata.version("soma-upgrade-prerequisites"),
)
def cli() -> None:
    """Automate dependency analysis, risk assessment, and progress tracking for elpaca upgrades."""

cli.add_command(preview_analysis)
cli.add_command(write_analysis)
cli.add_command(show_tracker)
cli.add_command(update_status)
cli.add_command(validate)
cli.add_command(update_note)
