#!/usr/bin/env python3
# Cascade computation and application for status propagation.
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from .constants import CascadeCandidate
from .progress_tracker import find_direct_dependents_any_status

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .models import ProgressTracker

# Statuses eligible for forward cascade blocking.
_CASCADE_ELIGIBLE = {"pending", "in-progress", "blocked"}


def compute_cascade_candidates(
    init_file: str,
    reverse_deps: Mapping[str, Sequence[str]],
    tracker: ProgressTracker,
) -> list[CascadeCandidate]:
    """Compute transitive dependents eligible for cascade blocking.

    Uses BFS via find_direct_dependents_any_status. Returns entries
    with pending, in-progress, or blocked status. Excludes upgraded,
    skipped, and reverted (deliberate user decisions). Pure function.
    """
    all_deps = _bfs_dependents(init_file, reverse_deps, tracker)
    status_map = {e.init_file: e.status for e in tracker.entries}
    return [
        CascadeCandidate(position=i, init_file=dep)
        for i, dep in enumerate(all_deps, 1)
        if status_map.get(dep) in _CASCADE_ELIGIBLE
    ]


def compute_all_transitive_dependents(
    init_file: str,
    reverse_deps: Mapping[str, Sequence[str]],
    tracker: ProgressTracker,
) -> list[CascadeCandidate]:
    """Compute ALL transitive dependents regardless of status.

    Same BFS as compute_cascade_candidates but without filtering.
    Used by show --dependents for rollback analysis. Pure function.
    """
    all_deps = _bfs_dependents(init_file, reverse_deps, tracker)
    return [
        CascadeCandidate(position=i, init_file=dep)
        for i, dep in enumerate(all_deps, 1)
    ]


def _bfs_dependents(
    init_file: str,
    reverse_deps: Mapping[str, Sequence[str]],
    tracker: ProgressTracker,
) -> list[str]:
    """BFS traversal of transitive dependents in the tracker."""
    visited: set[str] = set()
    result: list[str] = []
    queue: deque[str] = deque()
    for dep in find_direct_dependents_any_status(
        init_file, reverse_deps, tracker,
    ):
        if dep not in visited:
            visited.add(dep)
            queue.append(dep)
    while queue:
        current = queue.popleft()
        result.append(current)
        for dep in find_direct_dependents_any_status(
            current, reverse_deps, tracker,
        ):
            if dep not in visited:
                visited.add(dep)
                queue.append(dep)
    return result


def compute_reverse_cascade_candidates(
    init_file: str,
    tracker: ProgressTracker,
) -> list[str]:
    """Find all entries whose blocked_by list contains init_file.

    Returns their init file names. Pure, no mutation.
    """
    return [
        e.init_file for e in tracker.entries
        if init_file in e.blocked_by
    ]
