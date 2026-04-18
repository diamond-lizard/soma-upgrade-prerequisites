#!/usr/bin/env python3
# Tests for preserve_statuses function.
from __future__ import annotations

from soma_upgrade_prerequisites.tracker_preserve import preserve_statuses
from tests.tracker_test_helpers import make_entry, make_tracker


def test_preserves_terminal_statuses() -> None:
    """Terminal and in-progress statuses are preserved."""
    existing = make_tracker([
        make_entry("a.el", "upgraded", "done"),
        make_entry("b.el", "skipped", "skip reason"),
    ])
    new = make_tracker([make_entry("a.el"), make_entry("b.el")])
    result = preserve_statuses(new, existing, {})
    assert result.entries[0].status == "upgraded"
    assert result.entries[0].notes == "done"
    assert result.entries[1].status == "skipped"


def test_leaves_non_preserved_unchanged() -> None:
    """Pending entries in existing tracker are not preserved."""
    existing = make_tracker([make_entry("a.el", "pending")])
    new = make_tracker([make_entry("a.el")])
    result = preserve_statuses(new, existing, {})
    assert result.entries[0].status == "pending"


def test_blocked_by_sanitization_removes_invalid() -> None:
    """Blocked_by refs not in transitive deps are removed."""
    existing = make_tracker([
        make_entry("a.el", "blocked", blocked_by=["b.el", "c.el"]),
    ])
    new = make_tracker([make_entry("a.el")])
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    result = preserve_statuses(new, existing, dep_graph)
    assert result.entries[0].blocked_by == ["b.el"]
    assert result.entries[0].status == "blocked"


def test_blocked_by_empty_after_sanitization_resets() -> None:
    """Blocked entry resets to pending if blocked_by becomes empty."""
    existing = make_tracker([
        make_entry("a.el", "blocked", blocked_by=["gone.el"]),
    ])
    new = make_tracker([make_entry("a.el")])
    dep_graph = {"a.el": []}
    result = preserve_statuses(new, existing, dep_graph)
    assert result.entries[0].status == "pending"
    assert result.entries[0].blocked_by == []


def test_blocked_by_partial_removal() -> None:
    """Multiple blockers: valid ones kept, invalid ones removed."""
    existing = make_tracker([
        make_entry("a.el", "blocked", blocked_by=["b.el", "gone.el"]),
    ])
    new = make_tracker([make_entry("a.el")])
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    result = preserve_statuses(new, existing, dep_graph)
    assert result.entries[0].blocked_by == ["b.el"]
    assert result.entries[0].status == "blocked"
