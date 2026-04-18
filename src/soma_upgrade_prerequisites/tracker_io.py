#!/usr/bin/env python3
# Read and write operations for the progress tracker JSON file.
from __future__ import annotations

from typing import TYPE_CHECKING

from .defaults import TRACKER_SCHEMA_VERSION
from .models import ProgressTracker

if TYPE_CHECKING:
    from .protocols import FileSystem


def read_tracker(
    fs: FileSystem, tracker_path: str,
) -> ProgressTracker | None:
    """Read and parse the progress tracker JSON file.

    Returns None if the file does not exist. Raises ValueError
    if schema_version does not match.
    """
    if not fs.file_exists(tracker_path):
        return None
    content = fs.read_file(tracker_path)
    tracker = ProgressTracker.model_validate_json(content)
    if tracker.schema_version != TRACKER_SCHEMA_VERSION:
        msg = (
            f"Tracker schema version {tracker.schema_version} does not "
            f"match expected {TRACKER_SCHEMA_VERSION}. "
            "Please re-run `generate --write`."
        )
        raise ValueError(msg)
    return tracker


def write_tracker(
    fs: FileSystem,
    tracker_path: str,
    tracker: ProgressTracker,
    backup: bool,
) -> None:
    """Write tracker to disk with optional backup.

    If backup is True and the file exists, copies to <path>.bak first.
    """
    if backup and fs.file_exists(tracker_path):
        fs.copy_file(tracker_path, tracker_path + ".bak")
    fs.write_file(tracker_path, tracker.model_dump_json(indent=2))
