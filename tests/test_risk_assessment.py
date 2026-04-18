#!/usr/bin/env python3
# Tests for risk assessment functions.
from __future__ import annotations

from soma_upgrade_prerequisites.risk_assessment import list_upgrade_files
from tests.fakes import InMemoryFileSystem


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
