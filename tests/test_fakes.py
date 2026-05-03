#!/usr/bin/env python3
# Tests for fake implementations (InMemoryFileSystem, FakeGitClient).
from __future__ import annotations

import pytest

from soma_upgrade_prerequisites.protocols import GitBoundaryError
from tests.fake_git import FakeGitClient
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
