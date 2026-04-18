#!/usr/bin/env python3
# Tests for tracker-related validation functions.
from __future__ import annotations

from soma_upgrade_prerequisites.validation import validate_tracker_vs_sort
from tests.tracker_test_helpers import make_entry, make_tracker


def test_tracker_vs_sort_consistent() -> None:
    """Returns empty list when tracker matches the sort."""
    tracker = make_tracker([
        make_entry("a.el"),
        make_entry("b.el"),
    ])
    tracker.entries[0].order = 1
    tracker.entries[1].order = 2
    assert validate_tracker_vs_sort(tracker, ["a.el", "b.el"]) == []


def test_tracker_vs_sort_missing_from_tracker() -> None:
    """Detects init files in the sort missing from the tracker."""
    tracker = make_tracker([make_entry("a.el")])
    tracker.entries[0].order = 1
    errors = validate_tracker_vs_sort(tracker, ["a.el", "b.el"])
    assert any("b.el" in e and "missing" in e.lower() for e in errors)


def test_tracker_vs_sort_order_mismatch() -> None:
    """Detects order column mismatches."""
    tracker = make_tracker([
        make_entry("a.el"),
        make_entry("b.el"),
    ])
    tracker.entries[0].order = 2
    tracker.entries[1].order = 1
    errors = validate_tracker_vs_sort(tracker, ["a.el", "b.el"])
    assert len(errors) > 0


def test_tracker_vs_sort_orphaned_entry() -> None:
    """Detects tracker entries not in the sort."""
    tracker = make_tracker([
        make_entry("a.el"),
        make_entry("gone.el"),
    ])
    tracker.entries[0].order = 1
    tracker.entries[1].order = 2
    errors = validate_tracker_vs_sort(tracker, ["a.el"])
    assert any("gone.el" in e for e in errors)
