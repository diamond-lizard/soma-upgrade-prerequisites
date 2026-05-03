#!/usr/bin/env python3
# Tests for FakeGitClient.
from __future__ import annotations

import pytest

from soma_upgrade_prerequisites.protocols import GitBoundaryError
from tests.fake_git import FakeGitClient


def test_git_get_commit_hash() -> None:
    """get_commit_hash returns the configured hash."""
    git = FakeGitClient("abc123", [], "main")
    assert git.get_commit_hash("HEAD") == "abc123"


def test_git_get_commit_hash_error() -> None:
    """get_commit_hash raises ValueError when error configured."""
    git = FakeGitClient("x", [], "main", commit_hash_error="fail")
    with pytest.raises(ValueError, match="fail"):
        git.get_commit_hash("HEAD")


def test_git_get_log_lines() -> None:
    """get_log_lines returns stored lines for expected branch."""
    git = FakeGitClient("x", ["abc commit1", "def commit2"], "main")
    assert git.get_log_lines("main") == ["abc commit1", "def commit2"]


def test_git_get_log_lines_wrong_branch() -> None:
    """get_log_lines raises ValueError for unexpected branch."""
    git = FakeGitClient("x", [], "main")
    with pytest.raises(ValueError, match="failed"):
        git.get_log_lines("other")


def test_git_get_log_lines_since_returns_stored_lines() -> None:
    """get_log_lines_since returns configured log_lines_since list."""
    git = FakeGitClient("x", [], "main", log_lines_since=["abc commit1"])
    assert git.get_log_lines_since("main", "start") == ["abc commit1"]


def test_git_get_log_lines_since_wrong_branch_raises_value_error() -> None:
    """get_log_lines_since raises plain ValueError for wrong branch."""
    git = FakeGitClient("x", [], "main", log_lines_since=[])
    with pytest.raises(ValueError) as exc_info:
        git.get_log_lines_since("other", "start")
    assert type(exc_info.value) is not GitBoundaryError


def test_git_get_log_lines_since_raises_boundary_error() -> None:
    """get_log_lines_since raises GitBoundaryError when configured."""
    err = GitBoundaryError("not an ancestor")
    git = FakeGitClient("x", [], "main", log_lines_since_exception=err)
    with pytest.raises(GitBoundaryError, match="not an ancestor"):
        git.get_log_lines_since("main", "start")


def test_git_get_log_lines_since_raises_plain_value_error() -> None:
    """get_log_lines_since raises plain ValueError when configured."""
    err = ValueError("git infrastructure failure")
    git = FakeGitClient("x", [], "main", log_lines_since_exception=err)
    with pytest.raises(ValueError, match="git infrastructure failure") as exc_info:
        git.get_log_lines_since("main", "start")
    assert type(exc_info.value) is not GitBoundaryError


def test_git_get_log_lines_since_falls_back_to_log_lines() -> None:
    """get_log_lines_since uses _log_lines when log_lines_since is None."""
    git = FakeGitClient("x", ["abc fallback"], "main")
    assert git.get_log_lines_since("main", "start") == ["abc fallback"]


def test_git_get_log_lines_since_records_call() -> None:
    """get_log_lines_since appends call tuple to self.calls."""
    git = FakeGitClient("x", [], "main", log_lines_since=[])
    git.get_log_lines_since("main", "abc123")
    assert ("get_log_lines_since", "main", "abc123") in git.calls
