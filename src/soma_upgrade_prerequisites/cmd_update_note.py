#!/usr/bin/env python3
"""CLI subcommand: update-note (modify a tracker entry's note)."""
# CLI subcommand: update-note (modify a tracker entry's note).
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import click

from .defaults import DEFAULT_TRACKER_PATH

if TYPE_CHECKING:
    from .constants import Status
    from .models import ProgressTracker


@click.command("update-note")
@click.argument("init_file")
@click.option("--note", required=True, help="New note text for the entry.")
@click.option(
    "--tracker", default=DEFAULT_TRACKER_PATH, show_default=True,
    help="Path to the progress tracker JSON file.",
)
def update_note(init_file: str, note: str, tracker: str) -> None:
    """Update the note on a tracker entry without changing status."""
    import pydantic

    from .filesystem import RealFileSystem
    from .tracker_io import read_tracker, write_tracker
    from .tracker_update import update_entry

    fs = RealFileSystem()
    trk = read_tracker(fs, tracker)
    if trk is None:
        click.echo(
            "Tracker file not found. Run `write-analysis` first.",
            err=True,
        )
        sys.exit(1)
    try:
        updated = update_entry(
            trk, init_file, _current_status(trk, init_file),
            note=note, force=False, blocked_by=None,
        )
    except (ValueError, pydantic.ValidationError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    write_tracker(fs, tracker, updated, backup=True)
    click.echo(f"Updated note on {init_file}.")


def _current_status(trk: ProgressTracker, init_file: str) -> Status:
    """Look up current status of an entry by init_file."""
    for entry in trk.entries:
        if entry.init_file == init_file:
            return entry.status
    msg = f"Init file '{init_file}' not found in tracker"
    raise ValueError(msg)
