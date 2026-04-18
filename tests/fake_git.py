#!/usr/bin/env python3
# Fake git client for testing.
from __future__ import annotations


class FakeGitClient:
    """In-memory fake git client for testing."""

    def __init__(
        self,
        commit_hash: str,
        log_lines: list[str],
        branch: str,
        commit_hash_error: str | None = None,
    ) -> None:
        """Initialize with canned responses."""
        self._commit_hash = commit_hash
        self._log_lines = log_lines
        self._branch = branch
        self._commit_hash_error = commit_hash_error

    def get_commit_hash(self, ref: str) -> str:
        """Return stored hash or raise if error configured."""
        if self._commit_hash_error is not None:
            raise ValueError(self._commit_hash_error)
        return self._commit_hash

    def get_log_lines(self, branch: str) -> list[str]:
        """Return stored log lines for expected branch."""
        if branch != self._branch:
            msg = f"git log for branch '{branch}' failed"
            raise ValueError(msg)
        return list(self._log_lines)
