#!/usr/bin/env python3
# CLI entry point for soma-upgrade-prerequisites.
# Defines the click group and registers subcommands.
from __future__ import annotations

import importlib.metadata

import click

from .cmd_generate import generate


@click.group()
@click.version_option(
    version=importlib.metadata.version("soma-upgrade-prerequisites"),
)
def cli() -> None:
    """Automate dependency analysis, risk assessment, and progress tracking for elpaca upgrades."""


cli.add_command(generate)
