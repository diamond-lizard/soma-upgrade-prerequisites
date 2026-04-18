#!/usr/bin/env python3
# Tests for format_table detail lines, filters, and summary.
from __future__ import annotations

import click

from soma_upgrade_prerequisites.report_table import format_table
from tests.tracker_test_helpers import make_entry, make_tracker


def test_format_table_blocker_detail() -> None:
    """Entries with blockers show 'Blocked by' detail."""
    e = make_entry("a.el", "blocked", blocked_by=["b.el"])
    blocker = make_entry("b.el", "skipped")
    tracker = make_tracker([e, blocker])
    result = click.unstyle(format_table(tracker, None, False))
    assert "Blocked by" in result
    assert "b.el" in result
    assert "skipped" in result


def test_format_table_blocker_not_in_tracker() -> None:
    """Missing blocker shows '(not in tracker)' instead of crashing."""
    e = make_entry("a.el", "blocked", blocked_by=["gone.el"])
    tracker = make_tracker([e])
    result = click.unstyle(format_table(tracker, None, False))
    assert "gone.el (not in tracker)" in result


def test_format_table_notes_detail() -> None:
    """Entries with notes show 'Notes:' detail."""
    e = make_entry("a.el", notes="important note")
    tracker = make_tracker([e])
    result = click.unstyle(format_table(tracker, None, False))
    assert "Notes:" in result
    assert "important note" in result


def test_format_table_no_flags_no_brackets() -> None:
    """Entries with no flags omit brackets."""
    tracker = make_tracker([make_entry("a.el")])
    result = click.unstyle(format_table(tracker, None, False))
    assert "[" not in result


def test_format_table_summary_line() -> None:
    """Output begins with a summary line."""
    tracker = make_tracker([
        make_entry("a.el", "pending"),
        make_entry("b.el", "upgraded"),
    ])
    result = click.unstyle(format_table(tracker, None, False))
    first_line = result.splitlines()[0]
    assert "2 total" in first_line


def test_format_table_filtered_summary() -> None:
    """Filtered summary shows filtered count and total."""
    tracker = make_tracker([
        make_entry("a.el", "pending"),
        make_entry("b.el", "upgraded"),
    ])
    result = click.unstyle(format_table(tracker, "pending", False))
    first_line = result.splitlines()[0]
    assert "1 of 2" in first_line
