#!/usr/bin/env python3
# Pure status-update logic: apply status change with cascade.
from __future__ import annotations

from typing import TYPE_CHECKING

from .cascade import compute_reverse_cascade_candidates
from .cascade_apply import apply_forward_cascade, apply_reverse_cascade
from .constants import REVERSE_CASCADE_STATUSES
from .tracker_update import update_entry

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .constants import CascadeCandidate, Status
    from .models import ProgressTracker


def apply_status_update(
    tracker: ProgressTracker,
    init_file: str,
    status: Status,
    note: str | None,
    force: bool,
    forward_candidates: Sequence[CascadeCandidate] | None,
) -> tuple[ProgressTracker, str]:
    """Apply a status change with optional forward and reverse cascade.

    Pure function: no I/O, no prompting. Returns (updated_tracker,
    summary_string). The caller handles reading, confirmation, and
    writing.
    """
    previous = _get_previous_status(tracker, init_file)
    result = update_entry(tracker, init_file, status, note, force)
    result, fwd_count = _apply_forward(
        result, init_file, forward_candidates,
    )
    result, rev_count = _apply_reverse(
        result, init_file, previous, status,
    )
    summary = _build_summary(init_file, status, fwd_count, rev_count)
    return result, summary


def _get_previous_status(
    tracker: ProgressTracker, init_file: str,
) -> Status:
    """Look up the current status of an entry."""
    for entry in tracker.entries:
        if entry.init_file == init_file:
            return entry.status
    msg = f"Init file '{init_file}' not found in tracker"
    raise ValueError(msg)


def _apply_forward(
    tracker: ProgressTracker,
    init_file: str,
    candidates: Sequence[CascadeCandidate] | None,
) -> tuple[ProgressTracker, int]:
    """Apply forward cascade if candidates provided."""
    if candidates is None:
        return tracker, 0
    files = [c.init_file for c in candidates]
    return apply_forward_cascade(tracker, init_file, files), len(files)


def _apply_reverse(
    tracker: ProgressTracker,
    init_file: str,
    previous: Status,
    new: Status,
) -> tuple[ProgressTracker, int]:
    """Apply reverse cascade if transitioning away from cascade status."""
    if previous not in REVERSE_CASCADE_STATUSES:
        return tracker, 0
    if new in REVERSE_CASCADE_STATUSES:
        return tracker, 0
    candidates = compute_reverse_cascade_candidates(init_file, tracker)
    if not candidates:
        return tracker, 0
    return apply_reverse_cascade(tracker, init_file, candidates), len(candidates)


def _build_summary(
    init_file: str, status: Status,
    fwd_count: int, rev_count: int,
) -> str:
    """Build a human-readable summary of the status change."""
    parts = [f"Set {init_file} to {status}."]
    if fwd_count:
        parts.append(f"Cascade-blocked {fwd_count} dependent(s).")
    if rev_count:
        parts.append(f"Unblocked {rev_count} dependent(s).")
    return " ".join(parts)
