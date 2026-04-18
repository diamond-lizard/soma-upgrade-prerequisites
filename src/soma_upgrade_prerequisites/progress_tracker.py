#!/usr/bin/env python3
# Progress tracker creation, reading, updating, and writing.
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .defaults import STATUS_DEFINITIONS, TRACKER_SCHEMA_VERSION
from .models import ProgressTracker, TrackerEntry

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .constants import Flag
    from .models import DependencyGraph
    from .protocols import FileSystem


def create_tracker(
    starting_commit: str,
    sorted_files: Sequence[str],
    graph_data: DependencyGraph,
    levels: Mapping[str, int],
    flags: Mapping[str, Sequence[Flag]],
) -> ProgressTracker:
    """Build a new ProgressTracker from sorted init files.

    Each entry gets order (1-based), init_file, package (first in list),
    level, flags, status "pending", empty notes and blocked_by.
    """
    entries = [
        _make_entry(i, f, graph_data, levels, flags)
        for i, f in enumerate(sorted_files, 1)
    ]
    return ProgressTracker(
        schema_version=TRACKER_SCHEMA_VERSION,
        starting_commit=starting_commit,
        generated_at=datetime.now(tz=UTC).isoformat(),
        status_definitions=dict(STATUS_DEFINITIONS),
        entries=entries,
    )


def _make_entry(
    order: int,
    init_file: str,
    graph_data: DependencyGraph,
    levels: Mapping[str, int],
    flags: Mapping[str, Sequence[Flag]],
) -> TrackerEntry:
    """Build a single TrackerEntry."""
    package = graph_data[init_file].packages[0].package
    return TrackerEntry(
        order=order,
        init_file=init_file,
        package=package,
        level=levels.get(init_file, 0),
        flags=list(flags.get(init_file, [])),
        status="pending",
        notes="",
        blocked_by=[],
    )


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


def find_direct_dependents_any_status(
    init_file: str,
    reverse_deps: Mapping[str, Sequence[str]],
    tracker: ProgressTracker,
) -> list[str]:
    """Find all tracker entries that directly depend on init_file.

    Returns init files regardless of their current status.
    Used by compute_cascade_candidates to traverse through
    already-blocked nodes.
    """
    tracker_files = {e.init_file for e in tracker.entries}
    return [
        dep for dep in reverse_deps.get(init_file, [])
        if dep in tracker_files
    ]
