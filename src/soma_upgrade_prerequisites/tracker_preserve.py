#!/usr/bin/env python3
"""Status preservation during tracker regeneration."""
# Status preservation during tracker regeneration.
# Merges terminal and in-progress statuses from an existing tracker.
from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import PRESERVED_STATUSES

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .models import ProgressTracker, TrackerEntry

def preserve_statuses(
    new_tracker: ProgressTracker,
    existing_tracker: ProgressTracker,
    init_dep_graph: Mapping[str, Sequence[str]],
) -> ProgressTracker:
    """Merge preserved statuses from existing tracker into new one.

    Copies terminal and in-progress statuses, notes, and blocked_by.
    Sanitizes blocked_by against current transitive deps.
    Returns a new ProgressTracker; inputs are not modified.
    """
    existing_map = {
        e.init_file: e for e in existing_tracker.entries
    }
    result = new_tracker.model_copy(deep=True)
    for entry in result.entries:
        old = existing_map.get(entry.init_file)
        if old is None or old.status not in PRESERVED_STATUSES:
            continue
        _apply_preserved(entry, old, init_dep_graph)
    return result


def _apply_preserved(
    entry: TrackerEntry,
    old: TrackerEntry,
    init_dep_graph: Mapping[str, Sequence[str]],
) -> None:
    """Apply preserved status, notes, and sanitized blocked_by."""
    entry.status = old.status
    entry.notes = old.notes
    entry.blocked_by = list(old.blocked_by)
    if entry.status == "blocked":
        _sanitize_blocked_by(entry, init_dep_graph)


def _sanitize_blocked_by(
    entry: TrackerEntry,
    init_dep_graph: Mapping[str, Sequence[str]],
) -> None:
    """Remove blocked_by refs not in transitive dependency chain."""
    trans = _transitive_deps(entry.init_file, init_dep_graph)
    entry.blocked_by = [b for b in entry.blocked_by if b in trans]
    if not entry.blocked_by:
        entry.status = "pending"


def _transitive_deps(
    node: str, dep_graph: Mapping[str, Sequence[str]],
) -> set[str]:
    """Compute all transitive dependencies of a node."""
    visited: set[str] = set()
    stack = list(dep_graph.get(node, []))
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        stack.extend(dep_graph.get(current, []))
    return visited
