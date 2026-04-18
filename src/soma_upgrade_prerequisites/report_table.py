#!/usr/bin/env python3
# Table rendering for the progress tracker show subcommand.
# Condensed vertical layout with status colorization and filtering.
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from .report_entry import format_entry

if TYPE_CHECKING:
    from .models import ProgressTracker, TrackerEntry


def format_table(
    tracker: ProgressTracker,
    status_filter: str | None,
    flags_only: bool,
) -> str:
    """Format tracker as condensed vertical layout.

    Returns the formatted string with summary and entry lines.
    """
    filtered = _apply_filters(tracker.entries, status_filter, flags_only)
    if not filtered:
        return "No matching entries."
    summary = _build_summary(tracker, filtered, status_filter, flags_only)
    status_map = {e.init_file: e.status for e in tracker.entries}
    lines = [summary]
    for entry in filtered:
        lines.append(format_entry(entry, status_map))
    return "\n".join(lines)


def _apply_filters(
    entries: list[TrackerEntry],
    status_filter: str | None,
    flags_only: bool,
) -> list[TrackerEntry]:
    """Filter entries by status and/or flags."""
    result = entries
    if status_filter is not None:
        result = [e for e in result if e.status == status_filter]
    if flags_only:
        result = [e for e in result if e.flags]
    return result


def _build_summary(
    tracker: ProgressTracker,
    filtered: list[TrackerEntry],
    status_filter: str | None,
    flags_only: bool,
) -> str:
    """Build the summary line."""
    total = len(tracker.entries)
    counts = Counter(e.status for e in tracker.entries)
    parts = [f"{v} {k}" for k, v in sorted(counts.items())]
    base = f"{total} total: {', '.join(parts)}"
    if status_filter is None and not flags_only:
        return base
    filters: list[str] = []
    if status_filter:
        filters.append(f"status={status_filter}")
    if flags_only:
        filters.append("flags-only")
    return f"Showing {len(filtered)} of {total} (filter: {', '.join(filters)})"

