#!/usr/bin/env python3
# Integration tests for boundary-scoped validation.
from __future__ import annotations

import pytest

from soma_upgrade_prerequisites.protocols import GitBoundaryError

from .fake_git import FakeGitClient
from .tracker_test_helpers import make_entry, make_tracker
from .validate_test_helpers import run_with_fakes


def test_ac1_no_post_boundary_commits() -> None:
    """AC1: no commits after starting_commit means zero git discrepancies."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    git = FakeGitClient("abc", [], "main", log_lines_since=[])
    run_with_fakes(tracker, git)


def test_ac2_pending_with_current_round_commit() -> None:
    """AC2: current-round commit + pending entry reports discrepancy."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    git = FakeGitClient(
        "abc", [], "main",
        log_lines_since=["abc123 [a.el] Upgrade pkg from v1 to v2"],
    )
    with pytest.raises(SystemExit) as exc_info:
        run_with_fakes(tracker, git)
    assert exc_info.value.code == 1


def test_ac3_historical_commit_invisible() -> None:
    """AC3: pre-boundary commit for non-tracker file is invisible."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    git = FakeGitClient(
        "abc",
        ["old123 [old.el] Upgrade old from v1 to v2"],
        "main",
        log_lines_since=[],
    )
    run_with_fakes(tracker, git)
    assert ("get_log_lines_since", "main", "abc") in git.calls
    assert not any(c[0] == "get_log_lines" for c in git.calls)


def test_ac4_prior_round_commit_ignored() -> None:
    """AC4: prior-round commit for re-pending init file is ignored."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    git = FakeGitClient(
        "abc",
        ["old123 [a.el] Upgrade pkg from v0 to v1"],
        "main",
        log_lines_since=[],
    )
    run_with_fakes(tracker, git)


def test_ac5_boundary_error_plus_sort_error(capsys) -> None:
    """AC5: boundary error in git section AND sort error both reported."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="pending"),
    ])
    git = FakeGitClient(
        "abc", [], "main",
        log_lines_since_exception=GitBoundaryError("bad starting_commit"),
    )
    with pytest.raises(SystemExit) as exc_info:
        run_with_fakes(tracker, git, sorted_files=["b.el", "a.el"])
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "Tracker vs git:" in out
    assert "bad starting_commit" in out
    assert "Tracker vs sort:" in out


def test_ac5_fatal_value_error_propagates() -> None:
    """AC5-fatal: plain ValueError propagates, not caught by runner."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    git = FakeGitClient(
        "abc", [], "main",
        log_lines_since_exception=ValueError("git not installed"),
    )
    with pytest.raises(ValueError, match="git not installed"):
        run_with_fakes(tracker, git)


def test_boundary_equality_not_an_error() -> None:
    """Boundary equality: starting_commit == tip is valid, not an error."""
    tracker = make_tracker(
        [make_entry("a.el", status="pending")],
        starting_commit="tip_sha",
    )
    git = FakeGitClient("tip_sha", [], "main", log_lines_since=[])
    run_with_fakes(tracker, git)
