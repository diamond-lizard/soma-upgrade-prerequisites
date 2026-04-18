#!/usr/bin/env python3
# Concrete FileSystem implementation using pathlib and os.
# This is the production I/O layer; all other code uses the Protocol.
from __future__ import annotations

import contextlib
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

class RealFileSystem:
    """Production filesystem using pathlib, os, and shutil."""

    def list_files(self, directory: str | Path, pattern: str) -> list[str]:
        """Return matching basenames in directory."""
        return [p.name for p in Path(directory).expanduser().glob(pattern)]

    def file_exists(self, path: str | Path) -> bool:
        """Check whether a file exists."""
        return Path(path).expanduser().exists()

    def read_file(self, path: str | Path) -> str:
        """Read and return file content as a string."""
        return Path(path).expanduser().read_text()

    def write_file(self, path: str | Path, content: str) -> None:
        _atomic_write(Path(path).expanduser(), content)

    def copy_file(self, src: str | Path, dst: str | Path) -> None:
        """Copy file content from src to dst."""
        shutil.copy2(Path(src).expanduser(), Path(dst).expanduser())

    def grep_files(
        self, pattern: str, paths: Sequence[str | Path],
    ) -> dict[str, list[str]]:
        """Return dict mapping file paths to matching lines.

        Pattern is a regex matched case-insensitively.
        Raises FileNotFoundError if any path does not exist.
        """
        return _grep_all(pattern, paths)



def _atomic_write(target: Path, content: str) -> None:
    """Write content to target atomically via temp file and rename."""
    fd, tmp = tempfile.mkstemp(dir=str(target.parent))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, str(target))
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise

def _grep_one(pattern: str, path: Path) -> list[str]:
    """Return lines matching pattern in a single file."""
    return [
        line for line in path.read_text().splitlines()
        if re.search(pattern, line, re.IGNORECASE)
    ]


def _grep_all(
    pattern: str, paths: Sequence[str | Path],
) -> dict[str, list[str]]:
    """Return dict mapping file paths to matching lines."""
    result: dict[str, list[str]] = {}
    for p in paths:
        expanded = Path(p).expanduser()
        if not expanded.exists():
            msg = f"File not found: {p}"
            raise FileNotFoundError(msg)
        matches = _grep_one(pattern, expanded)
        if matches:
            result[str(p)] = matches
    return result
