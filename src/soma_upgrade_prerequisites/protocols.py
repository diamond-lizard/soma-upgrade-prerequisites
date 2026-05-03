#!/usr/bin/env python3
"""Protocol definitions for I/O boundary abstractions."""
# Protocol definitions for I/O boundary abstractions.
# All production code depends on these Protocols, not concrete implementations.
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


class FileSystem(Protocol):
    """Abstraction over filesystem operations for dependency injection."""

    def list_files(self, directory: str | Path, pattern: str) -> list[str]:
        """Return matching basenames in directory."""
        ...

    def file_exists(self, path: str | Path) -> bool:
        """Check whether a file exists."""
        ...

    def read_file(self, path: str | Path) -> str:
        """Read and return file content as a string."""
        ...

    def write_file(self, path: str | Path, content: str) -> None:
        """Write content to file atomically."""
        ...

    def grep_files(
        self, pattern: str, paths: Sequence[str | Path],
    ) -> dict[str, list[str]]:
        """Return dict mapping file paths to matching lines.

        Only includes files with at least one match.
        Pattern is a regex matched case-insensitively.
        Raises FileNotFoundError if any path does not exist.
        """
        ...

    def copy_file(self, src: str | Path, dst: str | Path) -> None:
        """Copy file content from src to dst."""
        ...


class GitBoundaryError(ValueError):
    """Boundary validation failure in get_log_lines_since.

    Raised when start_exclusive cannot be resolved to a commit or is not
    an ancestor of the target branch.  Caught non-fatally by the validation
    runner so that remaining checks can still proceed.

    Infrastructure errors (branch not found, git operational failures) use
    plain ValueError instead.
    """


class GitClient(Protocol):
    """Abstraction over git operations for dependency injection."""

    def get_commit_hash(self, ref: str) -> str:
        """Return the commit hash for the given ref."""
        ...

    def get_log_lines(self, branch: str) -> list[str]:
        """Return git log --oneline output as a list of strings."""
        ...

    def get_log_lines_since(self, branch: str, start_exclusive: str) -> list[str]:
        """Return git log --oneline output for commits after start_exclusive on branch.

        Raises GitBoundaryError for boundary validation failures
        (start_exclusive not found or not an ancestor of branch).
        Raises ValueError for git infrastructure errors.
        """
        ...
