#!/usr/bin/env python3
# Tests for cascade computation functions and update-status subcommand.
from __future__ import annotations

from soma_upgrade_prerequisites.cascade import (
    compute_all_transitive_dependents,
    compute_cascade_candidates,
)
from soma_upgrade_prerequisites.cascade_apply import (
    apply_forward_cascade,
    apply_reverse_cascade,
)
from soma_upgrade_prerequisites.constants import CascadeCandidate

from .tracker_test_helpers import make_entry, make_tracker


def _reverse_deps_chain() -> dict[str, list[str]]:
    """Build reverse deps: a.el -> b.el -> c.el chain."""
    return {"a.el": ["b.el"], "b.el": ["c.el"]}


def test_cascade_candidates_returns_pending_dependents() -> None:
    """(a) Transitive pending dependents are returned as CascadeCandidates."""
    tracker = make_tracker([
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="pending"),
        make_entry("c.el", status="pending"),
    ])
    result = compute_cascade_candidates("a.el", _reverse_deps_chain(), tracker)
    init_files = [c.init_file for c in result]
    assert "b.el" in init_files
    assert "c.el" in init_files
    assert all(isinstance(c, CascadeCandidate) for c in result)


def test_cascade_traverses_through_blocked_nodes() -> None:
    """(a2) BFS traverses through already-blocked nodes."""
    tracker = make_tracker([
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="blocked", blocked_by=["x.el"]),
        make_entry("c.el", status="pending"),
    ])
    result = compute_cascade_candidates("a.el", _reverse_deps_chain(), tracker)
    init_files = [c.init_file for c in result]
    assert "c.el" in init_files


def test_cascade_includes_already_blocked_nodes() -> None:
    """(a3) Already-blocked entries are in candidates for blocked_by update."""
    tracker = make_tracker([
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="blocked", blocked_by=["x.el"]),
    ])
    result = compute_cascade_candidates(
        "a.el", {"a.el": ["b.el"]}, tracker,
    )
    init_files = [c.init_file for c in result]
    assert "b.el" in init_files


def test_cascade_includes_in_progress_entries() -> None:
    """(a6) In-progress entries appear in candidates to be blocked."""
    tracker = make_tracker([
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="in-progress"),
    ])
    result = compute_cascade_candidates(
        "a.el", {"a.el": ["b.el"]}, tracker,
    )
    init_files = [c.init_file for c in result]
    assert "b.el" in init_files


def test_cascade_excludes_terminal_non_blocked() -> None:
    """Upgraded/skipped/reverted entries are excluded from cascade."""
    tracker = make_tracker([
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="upgraded"),
    ])
    result = compute_cascade_candidates(
        "a.el", {"a.el": ["b.el"]}, tracker,
    )
    assert result == []


def test_all_transitive_returns_all_statuses() -> None:
    """(a4) Returns ALL transitive dependents regardless of status."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="upgraded"),
        make_entry("c.el", status="skipped"),
        make_entry("d.el", status="reverted"),
        make_entry("e.el", status="in-progress"),
    ])
    reverse_deps = {
        "a.el": ["b.el", "c.el"],
        "c.el": ["d.el"],
        "d.el": ["e.el"],
    }
    result = compute_all_transitive_dependents(
        "a.el", reverse_deps, tracker,
    )
    init_files = [c.init_file for c in result]
    assert "b.el" in init_files
    assert "c.el" in init_files
    assert "d.el" in init_files
    assert "e.el" in init_files


def test_all_transitive_empty_when_no_dependents() -> None:
    """(a5) Returns empty list when no dependents exist."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    result = compute_all_transitive_dependents("a.el", {}, tracker)
    assert result == []

def test_reverse_cascade_unblocks_entry() -> None:
    """(f) Blocked entry is set to pending when blocker is removed."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="blocked", blocked_by=["a.el"]),
    ])
    result = apply_reverse_cascade(tracker, "a.el", ["b.el"])
    entry_b = next(e for e in result.entries if e.init_file == "b.el")
    assert entry_b.status == "pending"
    assert entry_b.blocked_by == []


def test_reverse_cascade_clears_blocked_by_preserves_status() -> None:
    """(f2) Non-blocked entry gets blocked_by cleared, status unchanged."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="skipped", blocked_by=["a.el"]),
    ])
    result = apply_reverse_cascade(tracker, "a.el", ["b.el"])
    entry_b = next(e for e in result.entries if e.init_file == "b.el")
    assert entry_b.status == "skipped"
    assert entry_b.blocked_by == []


def test_reverse_cascade_multiple_blockers_remains_blocked() -> None:
    """(g) Entry with multiple blockers stays blocked after one removed."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="blocked", blocked_by=["a.el", "x.el"]),
    ])
    result = apply_reverse_cascade(tracker, "a.el", ["b.el"])
    entry_b = next(e for e in result.entries if e.init_file == "b.el")
    assert entry_b.status == "blocked"
    assert entry_b.blocked_by == ["x.el"]

def test_cascade_dedup_blocked_to_skipped() -> None:
    """(h) Dedup: blocked->skipped, blocker already in blocked_by."""
    tracker = make_tracker([
        make_entry("a.el", status="blocked", blocked_by=["x.el"]),
        make_entry("b.el", status="blocked", blocked_by=["a.el"]),
    ])
    candidates = compute_cascade_candidates(
        "a.el", {"a.el": ["b.el"]}, tracker,
    )
    result = apply_forward_cascade(
        tracker, "a.el", [c.init_file for c in candidates],
    )
    entry_b = next(e for e in result.entries if e.init_file == "b.el")
    assert entry_b.blocked_by == ["a.el"]
    assert entry_b.notes == ""


def test_cascade_dedup_blocked_to_reverted() -> None:
    """(h2) Same dedup for blocked->reverted transition."""
    tracker = make_tracker([
        make_entry("a.el", status="blocked", blocked_by=["x.el"]),
        make_entry("b.el", status="blocked", blocked_by=["a.el"]),
    ])
    candidates = compute_cascade_candidates(
        "a.el", {"a.el": ["b.el"]}, tracker,
    )
    result = apply_forward_cascade(
        tracker, "a.el", [c.init_file for c in candidates],
    )
    entry_b = next(e for e in result.entries if e.init_file == "b.el")
    assert entry_b.blocked_by == ["a.el"]


def test_cascade_stacking_new_blocker() -> None:
    """(h3) New blocker added when A not yet in dependent's blocked_by."""
    tracker = make_tracker([
        make_entry("a.el", status="blocked", blocked_by=["x.el"]),
        make_entry("b.el", status="blocked", blocked_by=["x.el"]),
    ])
    candidates = compute_cascade_candidates(
        "a.el", {"a.el": ["b.el"]}, tracker,
    )
    result = apply_forward_cascade(
        tracker, "a.el", [c.init_file for c in candidates],
    )
    entry_b = next(e for e in result.entries if e.init_file == "b.el")
    assert "x.el" in entry_b.blocked_by
    assert "a.el" in entry_b.blocked_by
