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
        log_lines_since: list[str] | None = None,
        log_lines_since_exception: Exception | None = None,
    ) -> None:
        """Initialize with canned responses."""
        self._commit_hash = commit_hash
        self._log_lines = log_lines
        self._branch = branch
        self._commit_hash_error = commit_hash_error
        self._log_lines_since = log_lines_since
        self._log_lines_since_exception = log_lines_since_exception
        self.calls: list[tuple[str, ...]] = []

    def get_commit_hash(self, ref: str) -> str:
        """Return stored hash or raise if error configured."""
        self.calls.append(("get_commit_hash", ref))
        if self._commit_hash_error is not None:
            raise ValueError(self._commit_hash_error)
        return self._commit_hash

    def get_log_lines(self, branch: str) -> list[str]:
        """Return stored log lines for expected branch."""
        self.calls.append(("get_log_lines", branch))
        if branch != self._branch:
            msg = f"git log for branch '{branch}' failed"
            raise ValueError(msg)
        return list(self._log_lines)

    def get_log_lines_since(self, branch: str, start_exclusive: str) -> list[str]:
        """Return scoped log lines, simulating boundary-aware queries."""
        self.calls.append(("get_log_lines_since", branch, start_exclusive))
        if self._log_lines_since_exception is not None:
            raise self._log_lines_since_exception
        if branch != self._branch:
            msg = f"could not resolve branch '{branch}' to a commit"
            raise ValueError(msg)
        source = self._log_lines_since if self._log_lines_since is not None else self._log_lines
        return list(source)
