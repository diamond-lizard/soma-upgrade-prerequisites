#!/usr/bin/env python3
# Shared pytest fixtures for all test modules.
from __future__ import annotations

import json

import pytest

from tests.fake_git import FakeGitClient
from tests.fakes import InMemoryFileSystem

GRAPH_DATA: dict[str, object] = {
    "soma-magit-init.el": {
        "packages": [
            {
                "package": "magit",
                "depends_on": [],
                "repo_url": "https://github.com/magit/magit",
                "min_emacs_version": "26.1",
            },
        ],
        "depended_on_by": ["soma-forge-init.el"],
    },
    "soma-forge-init.el": {
        "packages": [
            {
                "package": "forge",
                "depends_on": ["magit"],
                "repo_url": "https://github.com/magit/forge",
                "min_emacs_version": "26.1",
            },
        ],
        "depended_on_by": [],
    },
}

UPGRADES_DIR = "upgrades"
INITS_DIR = "inits"
GRAPH_PATH = "graph.json"


@pytest.fixture()
def fake_fs() -> InMemoryFileSystem:
    """Return an InMemoryFileSystem with minimal test data."""
    files: dict[str, str] = {
        GRAPH_PATH: json.dumps(GRAPH_DATA),
        f"{UPGRADES_DIR}/soma-magit-init.el-upgrade-process.md": (
            "# Upgrade Process\n## 3. New Dependencies\nNone\n"
        ),
        f"{UPGRADES_DIR}/soma-forge-init.el-upgrade-process.md": (
            "# Upgrade Process\n## 3. New Dependencies\nNone\n"
        ),
        f"{UPGRADES_DIR}/soma-magit-init.el-security-review.md": (
            "# Security Review\nNo issues found.\n"
        ),
        f"{UPGRADES_DIR}/soma-forge-init.el-security-review.md": (
            "# Security Review\nNo issues found.\n"
        ),
    }
    return InMemoryFileSystem(files)


@pytest.fixture()
def fake_git() -> FakeGitClient:
    """Return a FakeGitClient with a known commit hash."""
    return FakeGitClient(
        commit_hash="abc1234",
        log_lines=[],
        branch="elpaca-upgrades",
    )
