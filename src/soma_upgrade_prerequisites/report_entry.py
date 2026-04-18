#!/usr/bin/env python3
"""Entry formatting for the progress tracker table."""
# Entry formatting for the progress tracker table.
# Renders individual entries with headers, blockers, and notes.
from __future__ import annotations

from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .models import TrackerEntry

def _style_status(status: str) -> str:
    """Apply click styling to a status string."""
    if status == "upgraded":
        return click.style(status, fg="green")
    if status == "in-progress":
        return click.style(status, fg="yellow")
    if status == "blocked":
        return click.style(status, fg="red")
    if status == "skipped":
        return click.style(status, dim=True)
    if status == "reverted":
        return click.style(status, fg="magenta")
    return status


def format_entry(entry: TrackerEntry, status_map: Mapping[str, str]) -> str:
    """Format a single entry with header and optional detail lines."""
    header = _build_header(entry)
    details = _build_details(entry, status_map)
    if details:
        return header + "\n" + "\n".join(details) + "\n"
    return header


def _build_header(entry: TrackerEntry) -> str:
    """Build the compact header line for an entry."""
    flags_str = f" [{', '.join(entry.flags)}]" if entry.flags else ""
    styled = _style_status(entry.status)
    return (
        f"#{entry.order}  {entry.init_file} ({entry.package}) "
        f"L{entry.level}{flags_str} \u2014 {styled}"
    )


def _build_details(
    entry: TrackerEntry, status_map: Mapping[str, str],
) -> list[str]:
    """Build detail lines for blockers and notes."""
    lines: list[str] = []
    if entry.blocked_by:
        lines.extend(_blocker_lines(entry.blocked_by, status_map))
    if entry.notes:
        lines.append(f"    Notes: {entry.notes}")
    return lines


def _blocker_lines(
    blocked_by: list[str], status_map: Mapping[str, str],
) -> list[str]:
    """Format blocked-by detail lines."""
    if len(blocked_by) == 1:
        desc = _blocker_desc(blocked_by[0], status_map)
        return [f"    Blocked by {desc}"]
    lines = ["    Blocked by:"]
    for b in blocked_by:
        lines.append(f"        {_blocker_desc(b, status_map)}")
    return lines


def _blocker_desc(name: str, status_map: Mapping[str, str]) -> str:
    """Format a single blocker reference."""
    status = status_map.get(name)
    if status is None:
        return f"{name} (not in tracker)"
    return f"{name}, which is currently {status}"
