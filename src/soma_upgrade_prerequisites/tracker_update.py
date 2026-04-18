#!/usr/bin/env python3
"""Entry-level status and note updates for the progress tracker."""
# Entry-level status and note updates for the progress tracker.
from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import TERMINAL_STATUSES

if TYPE_CHECKING:
    from .constants import Status
    from .models import ProgressTracker, TrackerEntry


def update_entry(
    tracker: ProgressTracker,
    init_file: str,
    status: Status,
    note: str | None,
    force: bool,
    blocked_by: list[str] | None = None,
) -> ProgressTracker:
    """Update a single entry's status and optional note.

    Returns a new ProgressTracker; the input is never modified.
    Raises ValueError if init_file is not found or if changing a
    terminal status without force=True.
    """
    result = tracker.model_copy(deep=True)
    entry = _find_entry(result, init_file)
    _check_terminal_guard(entry.status, status, force)
    entry.status = status
    if note is not None:
        entry.notes = note
    if blocked_by is not None:
        entry.blocked_by = blocked_by
    return result


def _find_entry(
    tracker: ProgressTracker, init_file: str,
) -> TrackerEntry:
    """Find an entry by init_file or raise ValueError."""
    for entry in tracker.entries:
        if entry.init_file == init_file:
            return entry
    msg = f"Init file '{init_file}' not found in tracker"
    raise ValueError(msg)


def _check_terminal_guard(
    current: Status, new: Status, force: bool,
) -> None:
    """Raise ValueError if changing terminal status without force."""
    if (
        not force
        and current in TERMINAL_STATUSES
        and new not in TERMINAL_STATUSES
    ):
        msg = (
            f"Cannot change terminal status '{current}' to "
            f"'{new}' without --force"
        )
        raise ValueError(msg)
