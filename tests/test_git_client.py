#!/usr/bin/env python3
# Tests for RealGitClient.get_log_lines_since using a temporary git repo.
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from soma_upgrade_prerequisites.git_client import RealGitClient
from soma_upgrade_prerequisites.protocols import GitBoundaryError


@pytest.fixture()
def git_repo(tmp_path):
    """Create a temporary git repo with two commits on test-branch."""
    cwd = tmp_path
    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)
    run("git", "init", "-b", "test-branch")
    run("git", "config", "user.name", "Test")
    run("git", "config", "user.email", "test@test.com")
    run("git", "config", "commit.gpgsign", "false")
    (cwd / "file.txt").write_text("initial")
    run("git", "add", ".")
    run("git", "commit", "-m", "initial commit")
    initial_sha = run("git", "rev-parse", "HEAD").stdout.strip()
    (cwd / "init.el").write_text("upgraded")
    run("git", "add", ".")
    run("git", "commit", "-m", "[init.el] Upgrade pkg from 1.0 to 2.0")
    return {"path": str(cwd), "initial_sha": initial_sha, "branch": "test-branch"}


def test_returns_commits_after_start(git_repo):
    """get_log_lines_since returns only commits after starting point."""
    client = RealGitClient(git_repo["path"])
    lines = client.get_log_lines_since(git_repo["branch"], git_repo["initial_sha"])
    assert len(lines) == 1
    assert "init.el" in lines[0]


def test_empty_when_start_equals_tip(git_repo):
    """get_log_lines_since returns empty list when start equals branch tip."""
    client = RealGitClient(git_repo["path"])
    tip = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=git_repo["path"], capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert client.get_log_lines_since(git_repo["branch"], tip) == []


def test_raises_boundary_error_for_bad_start(git_repo):
    """get_log_lines_since raises GitBoundaryError for nonexistent start."""
    client = RealGitClient(git_repo["path"])
    with pytest.raises(GitBoundaryError, match="starting_commit"):
        client.get_log_lines_since(git_repo["branch"], "nonexistent_ref_abc123")


def test_raises_value_error_for_bad_branch(git_repo):
    """get_log_lines_since raises plain ValueError for nonexistent branch."""
    client = RealGitClient(git_repo["path"])
    with pytest.raises(ValueError) as exc_info:
        client.get_log_lines_since("nonexistent_branch_xyz", git_repo["initial_sha"])
    assert type(exc_info.value) is not GitBoundaryError


def test_raises_boundary_error_for_non_ancestor(git_repo):
    """get_log_lines_since raises GitBoundaryError when start is not ancestor."""
    cwd = git_repo["path"]
    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)
    run("git", "checkout", "-b", "diverged", git_repo["initial_sha"])
    (Path(cwd) / "other.txt").write_text("diverged")
    run("git", "add", ".")
    run("git", "commit", "-m", "diverged commit")
    diverged_sha = run("git", "rev-parse", "HEAD").stdout.strip()
    run("git", "checkout", git_repo["branch"])
    client = RealGitClient(cwd)
    with pytest.raises(GitBoundaryError, match="not an ancestor"):
        client.get_log_lines_since(git_repo["branch"], diverged_sha)
