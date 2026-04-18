#!/usr/bin/env python3
# Tests for preserve_statuses function.
from __future__ import annotations

from soma_upgrade_prerequisites.models import (
    ProgressTracker,
    TrackerEntry,
)
from soma_upgrade_prerequisites.tracker_preserve import preserve_statuses


def _tracker(entries: list[TrackerEntry]) -> ProgressTracker:
    """Build a minimal ProgressTracker with given entries."""
    return ProgressTracker(
        schema_version=1,
        starting_commit="abc",
        generated_at="2026-01-01",
        status_definitions={},
        entries=entries,
    )


def _entry(
    init_file: str,
    status: str = "pending",
    notes: str = "",
    blocked_by: list[str] | None = None,
) -> TrackerEntry:
    """Build a minimal TrackerEntry."""
    return TrackerEntry(
        order=1,
        init_file=init_file,
        package="pkg",
        level=0,
        flags=[],
        status=status,
        notes=notes,
        blocked_by=blocked_by or [],
    )


def test_preserves_terminal_statuses() -> None:
    """Terminal and in-progress statuses are preserved."""
    existing = _tracker([
        _entry("a.el", "upgraded", "done"),
        _entry("b.el", "skipped", "skip reason"),
    ])
    new = _tracker([_entry("a.el"), _entry("b.el")])
    result = preserve_statuses(new, existing, {})
    assert result.entries[0].status == "upgraded"
    assert result.entries[0].notes == "done"
    assert result.entries[1].status == "skipped"


def test_leaves_non_preserved_unchanged() -> None:
    """Pending entries in existing tracker are not preserved."""
    existing = _tracker([_entry("a.el", "pending")])
    new = _tracker([_entry("a.el")])
    result = preserve_statuses(new, existing, {})
    assert result.entries[0].status == "pending"


def test_blocked_by_sanitization_removes_invalid() -> None:
    """Blocked_by refs not in transitive deps are removed."""
    existing = _tracker([
        _entry("a.el", "blocked", blocked_by=["b.el", "c.el"]),
    ])
    new = _tracker([_entry("a.el")])
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    result = preserve_statuses(new, existing, dep_graph)
    assert result.entries[0].blocked_by == ["b.el"]
    assert result.entries[0].status == "blocked"


def test_blocked_by_empty_after_sanitization_resets() -> None:
    """Blocked entry resets to pending if blocked_by becomes empty."""
    existing = _tracker([
        _entry("a.el", "blocked", blocked_by=["gone.el"]),
    ])
    new = _tracker([_entry("a.el")])
    dep_graph = {"a.el": []}
    result = preserve_statuses(new, existing, dep_graph)
    assert result.entries[0].status == "pending"
    assert result.entries[0].blocked_by == []


def test_blocked_by_partial_removal() -> None:
    """Multiple blockers: valid ones kept, invalid ones removed."""
    existing = _tracker([
        _entry("a.el", "blocked", blocked_by=["b.el", "gone.el"]),
    ])
    new = _tracker([_entry("a.el")])
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    result = preserve_statuses(new, existing, dep_graph)
    assert result.entries[0].blocked_by == ["b.el"]
    assert result.entries[0].status == "blocked"
