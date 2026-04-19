#!/usr/bin/env python3
"""CLI subcommand: show-tracker (render tracker as table or show dependents)."""
# CLI subcommand: show-tracker (render tracker as table or show dependents).
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import click

from .defaults import (
    DEFAULT_DERIVED_DATA_PATH,
    DEFAULT_GRAPH_JSON,
    DEFAULT_TRACKER_PATH,
)

if TYPE_CHECKING:
    from .constants import Status
    from .models import ProgressTracker
    from .protocols import FileSystem

_ALL_STATUSES: list[Status] = [
    "pending", "in-progress", "upgraded", "skipped", "blocked", "reverted",
]


@click.command("show-tracker")
@click.option("--tracker", default=DEFAULT_TRACKER_PATH, show_default=True)
@click.option(
    "--status", "status_filter", default=None,
    type=click.Choice(_ALL_STATUSES),
)
@click.option("--flags", is_flag=True, help="Show only flagged entries.")
@click.option("--dependents", default=None, help="Show dependents of INIT.")
@click.option("--derived-data", default=DEFAULT_DERIVED_DATA_PATH)
@click.option("--graph-json", default=DEFAULT_GRAPH_JSON)
def show_tracker(
    tracker: str, status_filter: str | None, flags: bool,
    dependents: str | None,
    derived_data: str, graph_json: str,
) -> None:
    """Display tracker entries or show dependents of an init file."""
    import pydantic

    from .filesystem import RealFileSystem
    from .tracker_io import read_tracker

    fs = RealFileSystem()
    try:
        trk = read_tracker(fs, tracker)
    except (ValueError, pydantic.ValidationError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    if trk is None:
        click.echo("Tracker not found. Run `write-analysis`.", err=True)
        sys.exit(1)
    if dependents is not None:
        _run_dependents(fs, trk, dependents, derived_data, graph_json)
    else:
        _run_table(trk, status_filter, flags)


def _run_table(
    trk: ProgressTracker, status_filter: str | None, flags: bool,
) -> None:
    """Render tracker as formatted table."""
    from .report_table import format_table

    click.echo(format_table(trk, status_filter, flags))


def _run_dependents(
    fs: FileSystem, trk: ProgressTracker, init_file: str,
    dd_path: str, graph_path: str,
) -> None:
    """Delegate to show_dependents module."""
    from .show_dependents import show_dependents

    show_dependents(fs, trk, init_file, dd_path, graph_path)
