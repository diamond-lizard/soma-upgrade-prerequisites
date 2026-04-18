#!/usr/bin/env python3
# Tests for risk assessment functions.
from __future__ import annotations

from soma_upgrade_prerequisites.risk_assessment import (
    find_high_risk_files,
    find_multi_package_files,
    find_warned_files,
)
from soma_upgrade_prerequisites.upgrade_set import list_upgrade_files
from tests.fakes import InMemoryFileSystem
from tests.helpers import make_graph, pkg


def test_list_upgrade_files() -> None:
    """Lists upgrade-process.md files and maps to init file names."""
    fs = InMemoryFileSystem({
        "upgrades/soma-magit-init.el-upgrade-process.md": "",
        "upgrades/soma-forge-init.el-upgrade-process.md": "",
        "upgrades/init.el-upgrade-process.md": "",
        "upgrades/soma-magit-init.el-security-review.md": "",
    })
    result = list_upgrade_files(fs, "upgrades")
    assert sorted(result) == [
        "init.el", "soma-forge-init.el", "soma-magit-init.el",
    ]


def test_find_warned_files() -> None:
    """Identifies files with warning patterns, maps to init names."""
    grep_results = {
        "upgrades/soma-magit-init.el-upgrade-process.md": [
            "Do not upgrade until v5 is stable",
        ],
        "upgrades/soma-forge-init.el-upgrade-process.md": [
            "Safe to upgrade",
        ],
    }
    result = find_warned_files(grep_results)
    assert "soma-magit-init.el" in result
    assert "soma-forge-init.el" not in result
    assert r"do not upgrade" in result["soma-magit-init.el"]


def test_find_high_risk_files() -> None:
    """Identifies security-review.md files with risk patterns."""
    grep_results = {
        "upgrades/soma-magit-init.el-security-review.md": [
            "CVE-2024-1234 found in dependency",
        ],
        "upgrades/soma-forge-init.el-security-review.md": [
            "No issues found",
        ],
    }
    result = find_high_risk_files(grep_results)
    assert "soma-magit-init.el" in result
    assert "soma-forge-init.el" not in result
    assert "CVE" in result["soma-magit-init.el"]


def test_find_multi_package_files() -> None:
    """Identifies init files with more than one package."""
    graph = make_graph({
        "soma-multi-init.el": {
            "packages": [pkg("pkg-a"), pkg("pkg-b")],
            "depended_on_by": [],
        },
        "soma-single-init.el": {
            "packages": [pkg("single")],
            "depended_on_by": [],
        },
    })
    result = find_multi_package_files(graph)
    assert result == {"soma-multi-init.el": 2}
