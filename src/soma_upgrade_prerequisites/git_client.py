#!/usr/bin/env python3
"""Concrete GitClient implementation using subprocess."""
# Concrete GitClient implementation using subprocess.
# This is the production git layer; all other code uses the Protocol.
from __future__ import annotations

import subprocess
from pathlib import Path

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

    def _rev_parse_commit(self, ref: str) -> str | None:
        """Try to resolve ref to a commit SHA; return None on failure."""
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            capture_output=True, text=True,
            cwd=Path(self._repo_path).expanduser(),
        )
        if result.returncode != 0:
            return None
        sha = result.stdout.strip()
        return sha or None

    def _verify_ancestry(
        self, start_ref: str, start_sha: str,
        branch_ref: str, branch_tip: str,
    ) -> None:
        """Verify start_sha is an ancestor of branch_tip.

        Exit code 0: confirmed. Exit code 1: not ancestor (GitBoundaryError).
        Exit code >1: git operational error (ValueError).
        """
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", start_sha, branch_tip],
            capture_output=True, text=True,
            cwd=Path(self._repo_path).expanduser(),
        )
        if result.returncode == 1:
            msg = f"starting_commit '{start_ref}' is not an ancestor of branch '{branch_ref}'"
            raise GitBoundaryError(msg)
        if result.returncode > 1:
            detail = result.stderr.strip()
            msg = f"git merge-base failed{': ' + detail if detail else ''}"
            raise ValueError(msg)

    def _log_range(self, start_sha: str, end_sha: str) -> list[str]:
        """Return log lines for the exclusive range between two resolved SHAs."""
        result = subprocess.run(
            ["git", "log", "--oneline", f"{start_sha}..{end_sha}"],
            capture_output=True, text=True,
            cwd=Path(self._repo_path).expanduser(),
        )
        if result.returncode != 0:
            detail = result.stderr.strip()
            msg = f"git log failed{': ' + detail if detail else ''}"
            raise ValueError(msg)
        return [line.strip() for line in result.stdout.splitlines()]

    def get_log_lines_since(self, branch: str, start_exclusive: str) -> list[str]:
        """Return log lines for commits after start_exclusive on branch.

        Validates boundary integrity. Raises GitBoundaryError for boundary
        failures, ValueError for infrastructure errors.
        """
        start_sha = self._rev_parse_commit(start_exclusive)
        if start_sha is None:
            msg = f"could not resolve starting_commit '{start_exclusive}' to a commit"
            raise GitBoundaryError(msg)
        branch_tip = self._rev_parse_commit(branch)
        if branch_tip is None:
            msg = f"could not resolve branch '{branch}' to a commit"
            raise ValueError(msg)
        self._verify_ancestry(start_exclusive, start_sha, branch, branch_tip)
        return self._log_range(start_sha, branch_tip)
