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
