#!/usr/bin/env python3
"""Concrete GitClient implementation using subprocess."""
# Concrete GitClient implementation using subprocess.
# This is the production git layer; all other code uses the Protocol.
from __future__ import annotations

import subprocess
from pathlib import Path

from ._git_helpers import log_range, rev_parse_commit, verify_ancestry
from .protocols import GitBoundaryError


class RealGitClient:
    """Production git client using subprocess."""

    def __init__(self, repo_path: str) -> None:
        """Store the repository path for git commands."""
        self._repo_path = repo_path

    def get_commit_hash(self, ref: str) -> str:
        """Return the commit hash for the given ref."""
        result = subprocess.run(
            ["git", "rev-parse", ref],
            capture_output=True,
            text=True,
            cwd=Path(self._repo_path).expanduser(),
        )
        if result.returncode != 0:
            msg = f"git ref '{ref}' not found"
            raise ValueError(msg)
        return result.stdout.strip()

    def get_log_lines(self, branch: str) -> list[str]:
        """Return git log --oneline output as a list of strings."""
        result = subprocess.run(
            ["git", "log", "--oneline", branch],
            capture_output=True,
            text=True,
            cwd=Path(self._repo_path).expanduser(),
        )
        if result.returncode != 0:
            msg = f"git log for branch '{branch}' failed"
            raise ValueError(msg)
        return [line.strip() for line in result.stdout.splitlines()]

    def get_log_lines_since(self, branch: str, start_exclusive: str) -> list[str]:
        """Return log lines for commits after start_exclusive on branch.

        Validates boundary integrity. Raises GitBoundaryError for boundary
        failures, ValueError for infrastructure errors.
        """
        cwd = Path(self._repo_path).expanduser()
        start_sha = rev_parse_commit(start_exclusive, cwd)
        if start_sha is None:
            msg = f"could not resolve starting_commit '{start_exclusive}' to a commit"
            raise GitBoundaryError(msg)
        branch_tip = rev_parse_commit(branch, cwd)
        if branch_tip is None:
            msg = f"could not resolve branch '{branch}' to a commit"
            raise ValueError(msg)
        verify_ancestry(start_exclusive, start_sha, branch, branch_tip, cwd)
        return log_range(start_sha, branch_tip, cwd)
