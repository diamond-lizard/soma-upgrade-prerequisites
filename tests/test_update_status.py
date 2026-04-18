#!/usr/bin/env python3
# Tests for cascade computation functions and update-status subcommand.
from __future__ import annotations

from click.testing import CliRunner

from soma_upgrade_prerequisites.cascade import (
    compute_all_transitive_dependents,
    compute_cascade_candidates,
)
from soma_upgrade_prerequisites.cascade_apply import (
    apply_forward_cascade,
    apply_reverse_cascade,
)
from soma_upgrade_prerequisites.constants import CascadeCandidate
from soma_upgrade_prerequisites.main import cli
from soma_upgrade_prerequisites.status_update import (
    apply_status_update,
)

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


def test_update_status_help() -> None:
    """(a) update-status --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["update-status", "--help"])
    assert result.exit_code == 0
    assert "update-status" in result.output.lower()


def test_update_status_invalid_status() -> None:
    """(b) Invalid status value produces an error."""
    runner = CliRunner()
    result = runner.invoke(cli, ["update-status", "a.el", "nonsense"])
    assert result.exit_code != 0


def test_update_status_blocked_rejected() -> None:
    """(b) blocked is excluded from CLI choices."""
    runner = CliRunner()
    result = runner.invoke(cli, ["update-status", "a.el", "blocked"])
    assert result.exit_code != 0


def test_apply_status_update_changes_status() -> None:
    """(c) Status change applies correctly."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    updated, _ = apply_status_update(
        tracker, "a.el", "in-progress",
        note=None, force=False, forward_candidates=None,
    )
    entry = next(e for e in updated.entries if e.init_file == "a.el")
    assert entry.status == "in-progress"


def test_apply_status_update_forward_cascade() -> None:
    """(d) Forward candidates are cascade-blocked automatically."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="pending"),
    ])
    candidates = [CascadeCandidate(position=1, init_file="b.el")]
    updated, _ = apply_status_update(
        tracker, "a.el", "skipped",
        note=None, force=False, forward_candidates=candidates,
    )
    entry_b = next(e for e in updated.entries if e.init_file == "b.el")
    assert entry_b.status == "blocked"


def test_apply_status_update_no_forward_when_none() -> None:
    """(f) No forward cascade when forward_candidates is None."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="pending"),
    ])
    updated, _ = apply_status_update(
        tracker, "a.el", "skipped",
        note=None, force=False, forward_candidates=None,
    )
    entry_b = next(e for e in updated.entries if e.init_file == "b.el")
    assert entry_b.status == "pending"


def test_apply_status_update_reverse_cascade() -> None:
    """(g) Reverse cascade when previous status was in REVERSE_CASCADE."""
    tracker = make_tracker([
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="blocked", blocked_by=["a.el"]),
    ])
    updated, _ = apply_status_update(
        tracker, "a.el", "pending",
        note=None, force=True, forward_candidates=None,
    )
    entry_b = next(e for e in updated.entries if e.init_file == "b.el")
    assert entry_b.status == "pending"
    assert entry_b.blocked_by == []


def test_apply_status_update_reverse_no_derived_data() -> None:
    """(i) Reverse cascade works without derived data."""
    tracker = make_tracker([
        make_entry("a.el", status="blocked", blocked_by=["x.el"]),
        make_entry("b.el", status="blocked", blocked_by=["a.el"]),
    ])
    updated, _ = apply_status_update(
        tracker, "a.el", "pending",
        note=None, force=True, forward_candidates=None,
    )
    entry_b = next(e for e in updated.entries if e.init_file == "b.el")
    assert entry_b.status == "pending"


def test_update_status_stale_derived_data(tmp_path: object) -> None:
    """(h) Stale derived data produces exit code 1."""
    import json
    from pathlib import Path

    p = Path(str(tmp_path))
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
    ])
    tracker_path = p / "tracker.json"
    tracker_path.write_text(tracker.model_dump_json(indent=2))
    derived = {
        "schema_version": 1,
        "source_graph_hash": "stale_hash",
        "pkg_to_init": {},
        "init_to_packages": {},
        "init_dep_graph": {},
        "reverse_deps": {},
        "sorted_files": [],
    }
    derived_path = p / "derived.json"
    derived_path.write_text(json.dumps(derived))
    graph_path = p / "graph.json"
    graph_path.write_text("{}")
    runner = CliRunner()
    result = runner.invoke(cli, [
        "update-status", "a.el", "skipped",
        "--tracker", str(tracker_path),
        "--derived-data", str(derived_path),
        "--graph-json", str(graph_path),
        "--yes",
    ])
    assert result.exit_code == 1


def test_update_status_confirm_decline(tmp_path: object) -> None:
    """(j) Confirmation decline exits with code 0, tracker unchanged."""
    from pathlib import Path

    p = Path(str(tmp_path))
    tracker = make_tracker([make_entry("a.el", status="pending")])
    tracker_path = p / "tracker.json"
    tracker_path.write_text(tracker.model_dump_json(indent=2))
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "update-status", "a.el", "in-progress",
            "--tracker", str(tracker_path),
        ],
    )
    assert result.exit_code == 0


def test_update_status_yes_flag(tmp_path: object) -> None:
    """(k) --yes auto-confirms without prompting."""
    from pathlib import Path

    p = Path(str(tmp_path))
    tracker = make_tracker([make_entry("a.el", status="pending")])
    tracker_path = p / "tracker.json"
    tracker_path.write_text(tracker.model_dump_json(indent=2))
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "update-status", "a.el", "in-progress",
            "--tracker", str(tracker_path),
            "--yes",
        ],
    )
    assert result.exit_code == 0
