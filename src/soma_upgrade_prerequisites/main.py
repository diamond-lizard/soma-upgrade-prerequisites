#!/usr/bin/env python3
"""CLI entry point for soma-upgrade-prerequisites."""
# CLI entry point for soma-upgrade-prerequisites.
# Defines the click group and registers subcommands.
from __future__ import annotations

import importlib.metadata

import click

from .cmd_generate import generate
from .cmd_show import show
from .cmd_update_note import update_note
from .cmd_update_status import update_status
from .cmd_validate import validate


@click.group()
@click.version_option(
    version=importlib.metadata.version("soma-upgrade-prerequisites"),
)
def cli() -> None:
    """Automate dependency analysis, risk assessment, and progress tracking for elpaca upgrades."""

cli.add_command(generate)
cli.add_command(show)
cli.add_command(update_status)
cli.add_command(validate)
cli.add_command(update_note)
