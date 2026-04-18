#!/usr/bin/env python3
# Tests for find_new_deps_files.
from __future__ import annotations

from soma_upgrade_prerequisites.new_deps import find_new_deps_files
from tests.fakes import InMemoryFileSystem


def test_find_new_deps_files_non_empty_section() -> None:
    """Files with non-empty New Dependencies section are included."""
    fs = InMemoryFileSystem({
        "upgrades/a.el-upgrade-process.md": (
            "## 3. New Dependencies\nnew-package v1.0\n"
        ),
        "upgrades/b.el-upgrade-process.md": (
            "## 3. New Dependencies\nNone\n"
        ),
    })
    result = find_new_deps_files(fs, "upgrades", ["a.el", "b.el"])
    assert result == ["a.el"]


def test_find_new_deps_missing_header() -> None:
    """Files missing the header are treated as no new deps."""
    fs = InMemoryFileSystem({
        "upgrades/a.el-upgrade-process.md": "# No such section\n",
    })
    assert find_new_deps_files(fs, "upgrades", ["a.el"]) == []


def test_find_new_deps_empty_section() -> None:
    """Sections with only whitespace are treated as no new deps."""
    fs = InMemoryFileSystem({
        "upgrades/a.el-upgrade-process.md": (
            "## 3. New Dependencies\n\n\n## 4. Next\n"
        ),
    })
    assert find_new_deps_files(fs, "upgrades", ["a.el"]) == []


def test_find_new_deps_list_marker_false_positive() -> None:
    """Known limitation: '- None' is treated as having new deps."""
    fs = InMemoryFileSystem({
        "upgrades/a.el-upgrade-process.md": (
            "## 3. New Dependencies\n- None\n"
        ),
    })
    # The list marker prevents "none" pattern from matching
    result = find_new_deps_files(fs, "upgrades", ["a.el"])
    assert result == ["a.el"]
