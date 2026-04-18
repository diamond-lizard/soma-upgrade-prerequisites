#!/usr/bin/env python3
# Fake implementations of FileSystem and GitClient for testing.
# These are minimal working implementations, not mocks (REQ-4000).
from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class InMemoryFileSystem:
    """In-memory fake filesystem backed by a dict."""

    def __init__(self, files: dict[str, str] | None = None) -> None:
        """Initialize with optional pre-populated file contents."""
        self.files: dict[str, str] = dict(files) if files else {}

    def list_files(
        self, directory: str, pattern: str,
    ) -> list[str]:
        """Return basenames matching pattern in directory."""
        prefix = directory.rstrip("/") + "/"
        return [
            PurePosixPath(k).name
            for k in self.files
            if k.startswith(prefix)
            and fnmatch(PurePosixPath(k).name, pattern)
        ]

    def file_exists(self, path: str) -> bool:
        """Check whether a file exists in the store."""
        return str(path) in self.files

    def read_file(self, path: str) -> str:
        """Return stored file content or raise FileNotFoundError."""
        key = str(path)
        if key not in self.files:
            msg = f"File not found: {path}"
            raise FileNotFoundError(msg)
        return self.files[key]

    def write_file(self, path: str, content: str) -> None:
        """Store content in the backing dict."""
        self.files[str(path)] = content

    def copy_file(self, src: str, dst: str) -> None:
        """Copy stored content from src to dst."""
        key = str(src)
        if key not in self.files:
            msg = f"File not found: {src}"
            raise FileNotFoundError(msg)
        self.files[str(dst)] = self.files[key]

    def grep_files(
        self, pattern: str, paths: Sequence[str],
    ) -> dict[str, list[str]]:
        """Search stored files for lines matching pattern.

        Raises FileNotFoundError if any path is absent.
        """
        _check_paths_exist(paths, self.files)
        return _grep_stored(pattern, paths, self.files)



def _check_paths_exist(
    paths: Sequence[str], files: dict[str, str],
) -> None:
    """Raise FileNotFoundError if any path is absent from files."""
    for p in paths:
        if str(p) not in files:
            msg = f"File not found: {p}"
            raise FileNotFoundError(msg)

def _grep_stored(
    pattern: str, paths: Sequence[str], files: dict[str, str],
) -> dict[str, list[str]]:
    """Search stored file contents for lines matching pattern."""
    result: dict[str, list[str]] = {}
    for p in paths:
        key = str(p)
        matches = [
            line for line in files[key].splitlines()
            if re.search(pattern, line, re.IGNORECASE)
        ]
        if matches:
            result[key] = matches
    return result
