#!/usr/bin/env python3
# Tests for format_table (condensed vertical layout).
from __future__ import annotations

import click

from soma_upgrade_prerequisites.report_table import format_table
from tests.tracker_test_helpers import make_entry, make_tracker


def test_format_table_basic_layout() -> None:
    """Header line has correct format."""
    tracker = make_tracker([make_entry("a.el", flags=["warned"])])
    tracker.entries[0].order = 1
    tracker.entries[0].package = "pkg-a"
    result = click.unstyle(format_table(tracker, None, False))
    assert "#1  a.el (pkg-a) L0 [warned]" in result
    assert "pending" in result


def test_format_table_status_filter() -> None:
    """status_filter includes only matching entries."""
    tracker = make_tracker([
        make_entry("a.el", "pending"),
        make_entry("b.el", "upgraded"),
    ])
    result = click.unstyle(format_table(tracker, "pending", False))
    assert "a.el" in result
    assert "b.el" not in result


def test_format_table_flags_only() -> None:
    """flags_only includes only flagged entries."""
    tracker = make_tracker([
        make_entry("a.el", flags=["warned"]),
        make_entry("b.el"),
    ])
    result = click.unstyle(format_table(tracker, None, True))
    assert "a.el" in result
    assert "b.el" not in result


def test_format_table_no_matches() -> None:
    """No matching entries returns 'No matching entries.'"""
    tracker = make_tracker([make_entry("a.el", "pending")])
    result = format_table(tracker, "upgraded", False)
    assert result == "No matching entries."


