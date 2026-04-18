#!/usr/bin/env python3
"""CLI subcommand: update-status (modify tracker entry status with cascade)."""
# CLI subcommand: update-status (modify tracker entry status with cascade).
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import click

from .constants import FORWARD_CASCADE_STATUSES
from .defaults import (
    DEFAULT_DERIVED_DATA_PATH,
    DEFAULT_GRAPH_JSON,
    DEFAULT_TRACKER_PATH,
)
from .status_update import apply_status_update

if TYPE_CHECKING:
    from .constants import CascadeCandidate, Status
    from .models import ProgressTracker
    from .protocols import FileSystem

_STATUS_CHOICES: list[Status] = [
    "pending", "in-progress", "upgraded", "skipped", "reverted",
]


@click.command("update-status")
@click.argument("init_file")
@click.argument("status", type=click.Choice(_STATUS_CHOICES))
@click.option("--note", default=None, help="Note to attach.")
@click.option("--force", is_flag=True, help="Allow terminal->non-terminal.")
@click.option("--yes", "-y", is_flag=True, help="Auto-confirm cascade.")
@click.option("--tracker", default=DEFAULT_TRACKER_PATH, show_default=True)
@click.option("--derived-data", default=DEFAULT_DERIVED_DATA_PATH)
@click.option("--graph-json", default=DEFAULT_GRAPH_JSON)
def update_status(
    init_file: str, status: Status, note: str | None,
    force: bool, yes: bool,
    tracker: str, derived_data: str, graph_json: str,
) -> None:
    """Change a tracker entry's status with automatic cascade."""
    import pydantic

    from .filesystem import RealFileSystem
    from .tracker_io import read_tracker, write_tracker

    fs = RealFileSystem()
    trk = read_tracker(fs, tracker)
    if trk is None:
        click.echo("Tracker not found. Run `generate --write`.", err=True)
        sys.exit(1)
    if not any(e.init_file == init_file for e in trk.entries):
        click.echo(f"Init file '{init_file}' not found.", err=True)
        sys.exit(1)
    try:
        fwd = _load_forward(
            fs, status, init_file, derived_data, graph_json, trk,
        )
        if fwd and not yes:
            _show_cascade_and_confirm(fwd)
        updated, summary = apply_status_update(
            trk, init_file, status, note, force, fwd,
        )
        write_tracker(fs, tracker, updated, backup=True)
        click.echo(summary)
    except (ValueError, pydantic.ValidationError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


def _load_forward(
    fs: FileSystem, status: Status, init_file: str,
    dd_path: str, graph_path: str, trk: ProgressTracker,
) -> list[CascadeCandidate] | None:
    """Load derived data and compute forward cascade candidates."""
    if status not in FORWARD_CASCADE_STATUSES:
        return None
    from .cascade import compute_cascade_candidates
    from .derived_data import read_derived_data
    from .validation_git import check_stale_derived_data

    dd = read_derived_data(fs, dd_path)
    if dd is None:
        msg = "Derived data not found. Run `generate --write` first."
        raise ValueError(msg)
    check_stale_derived_data(fs.read_file(graph_path), dd)
    return compute_cascade_candidates(init_file, dd.reverse_deps, trk)


def _show_cascade_and_confirm(
    candidates: list[CascadeCandidate],
) -> None:
    """Show cascade preview and prompt for confirmation; exit 0 if declined."""
    click.echo(f"Will cascade-block {len(candidates)} dependent(s):")
    for c in candidates:
        click.echo(f"  - {c.init_file}")
    if not click.confirm("Proceed?"):
        sys.exit(0)
