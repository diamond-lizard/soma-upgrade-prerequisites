#!/usr/bin/env python3
"""Cascade application: forward blocking and reverse unblocking."""
# Cascade application: forward blocking and reverse unblocking.
from __future__ import annotations

from typing import TYPE_CHECKING

from .tracker_update import update_entry

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .models import ProgressTracker

# Statuses eligible for forward cascade status change.
_BLOCKABLE = {"pending", "in-progress"}


def apply_forward_cascade(
    tracker: ProgressTracker,
    blocking_init_file: str,
    selected_entries: Sequence[str],
) -> ProgressTracker:
    """Apply forward cascade blocking to selected entries.

    For each entry: if blocker already in blocked_by, skip (dedup).
    If pending/in-progress, set to blocked. If already blocked,
    append blocker to blocked_by (cascade stacking). Returns new
    tracker; input is not modified.
    """
    result = tracker
    for init_file in selected_entries:
        result = _cascade_one(result, blocking_init_file, init_file)
    return result


def _cascade_one(
    tracker: ProgressTracker,
    blocking_init_file: str,
    init_file: str,
) -> ProgressTracker:
    """Apply cascade to a single entry."""
    entry = next(e for e in tracker.entries if e.init_file == init_file)
    if blocking_init_file in entry.blocked_by:
        return tracker
    new_blocked_by = [*entry.blocked_by, blocking_init_file]
    if entry.status in _BLOCKABLE:
        return update_entry(
            tracker, init_file, "blocked",
            note=None, force=False, blocked_by=new_blocked_by,
        )
    if entry.status == "blocked":
        return update_entry(
            tracker, init_file, entry.status,
            note=None, force=False, blocked_by=new_blocked_by,
        )
    msg = f"Unexpected status '{entry.status}' for cascade target"
    raise ValueError(msg)


def apply_reverse_cascade(
    tracker: ProgressTracker,
    unblocked_init_file: str,
    candidates: Sequence[str],
) -> ProgressTracker:
    """Apply reverse cascade: remove blocker from blocked_by lists.

    If blocked_by becomes empty and status is blocked, set to pending.
    If blocked_by becomes empty but status is not blocked, clear
    blocked_by only (preserving user's deliberate status).
    Returns new tracker; input is not modified.
    """
    result = tracker
    for init_file in candidates:
        result = _unblock_one(result, unblocked_init_file, init_file)
    return result


def _unblock_one(
    tracker: ProgressTracker,
    unblocked_init_file: str,
    init_file: str,
) -> ProgressTracker:
    """Remove one blocker from a single entry's blocked_by."""
    entry = next(e for e in tracker.entries if e.init_file == init_file)
    new_blocked_by = [
        b for b in entry.blocked_by if b != unblocked_init_file
    ]
    if not new_blocked_by and entry.status == "blocked":
        return update_entry(
            tracker, init_file, "pending",
            note=None, force=True, blocked_by=[],
        )
    return update_entry(
        tracker, init_file, entry.status,
        note=None, force=False, blocked_by=new_blocked_by,
    )
