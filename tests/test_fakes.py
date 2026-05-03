#!/usr/bin/env python3
# Tests for fake implementations (InMemoryFileSystem).
from __future__ import annotations

import pytest

from tests.fakes import InMemoryFileSystem


def test_list_files_filters_by_directory_and_pattern() -> None:
    """list_files returns basenames matching pattern in directory."""
    fs = InMemoryFileSystem({
        "dir/a-upgrade-process.md": "",
        "dir/b-upgrade-process.md": "",
        "dir/c-security-review.md": "",
        "other/d-upgrade-process.md": "",
    })
    result = fs.list_files("dir", "*-upgrade-process.md")
    assert sorted(result) == [
        "a-upgrade-process.md", "b-upgrade-process.md",
    ]


def test_file_exists_present_and_absent() -> None:
    """file_exists returns True for present, False for absent."""
    fs = InMemoryFileSystem({"a.txt": "hello"})
    assert fs.file_exists("a.txt") is True
    assert fs.file_exists("missing.txt") is False


def test_write_then_read() -> None:
    """write_file stores content retrievable by read_file."""
    fs = InMemoryFileSystem()
    fs.write_file("new.txt", "content")
    assert fs.read_file("new.txt") == "content"


def test_read_missing_raises() -> None:
    """read_file raises FileNotFoundError for absent keys."""
    fs = InMemoryFileSystem()
    with pytest.raises(FileNotFoundError):
        fs.read_file("missing.txt")


def test_copy_file_copies_content() -> None:
    """copy_file duplicates content from src to dst."""
    fs = InMemoryFileSystem({"src.txt": "data"})
    fs.copy_file("src.txt", "dst.txt")
    assert fs.read_file("dst.txt") == "data"


def test_copy_file_missing_raises() -> None:
    """copy_file raises FileNotFoundError for absent source."""
    fs = InMemoryFileSystem()
    with pytest.raises(FileNotFoundError):
        fs.copy_file("missing.txt", "dst.txt")


def test_grep_files_finds_matches_case_insensitively() -> None:
    """grep_files returns matching lines case-insensitively."""
    fs = InMemoryFileSystem({
        "a.md": "Do Not Upgrade\nSafe line\n",
        "b.md": "no matches here\n",
    })
    result = fs.grep_files("do not upgrade", ["a.md", "b.md"])
    assert result == {"a.md": ["Do Not Upgrade"]}


def test_grep_files_missing_path_raises() -> None:
    """grep_files raises FileNotFoundError for absent paths."""
    fs = InMemoryFileSystem({"a.md": "content"})
    with pytest.raises(FileNotFoundError):
        fs.grep_files("pattern", ["a.md", "missing.md"])

