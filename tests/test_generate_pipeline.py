#!/usr/bin/env python3
# Integration tests for run_generate_pipeline.
from __future__ import annotations

import json

import click

from soma_upgrade_prerequisites.config import PipelineConfig
from soma_upgrade_prerequisites.pipeline import run_generate_pipeline
from tests.fake_git import FakeGitClient
from tests.fakes import InMemoryFileSystem
from tests.helpers import pkg

GRAPH = {
    "soma-magit-init.el": {
        "packages": [pkg("magit")],
        "depended_on_by": ["soma-forge-init.el"],
    },
    "soma-forge-init.el": {
        "packages": [pkg("forge", ["magit"])],
        "depended_on_by": [],
    },
}

CONFIG = PipelineConfig(
    graph_json_path="graph.json",
    upgrades_dir="upgrades",
    inits_dir="inits",
    branch="elpaca-upgrades",
    tracker_path="tracker.json",
    derived_data_path="derived.json",
)


def _make_fs() -> InMemoryFileSystem:
    """Build a filesystem with valid test data."""
    return InMemoryFileSystem({
        "graph.json": json.dumps(GRAPH),
        "upgrades/soma-magit-init.el-upgrade-process.md": (
            "# Upgrade\n## 3. New Dependencies\nNone\n"
        ),
        "upgrades/soma-forge-init.el-upgrade-process.md": (
            "# Upgrade\n## 3. New Dependencies\nNone\n"
        ),
        "upgrades/soma-magit-init.el-security-review.md": (
            "# Security\nNo issues.\n"
        ),
        "upgrades/soma-forge-init.el-security-review.md": (
            "# Security\nNo issues.\n"
        ),
    })


def _make_git() -> FakeGitClient:
    """Build a git client with valid test data."""
    return FakeGitClient("abc1234", [], "elpaca-upgrades")


def test_dry_run_writes_no_files() -> None:
    """Dry-run returns a report and writes no files."""
    fs = _make_fs()
    report, code = run_generate_pipeline(
        fs, _make_git(), CONFIG, write=False, existing_tracker=None,
    )
    assert code == 0
    assert "tracker.json" not in fs.files
    assert "derived.json" not in fs.files
    plain = click.unstyle(report)
    assert "Generate Summary" in plain


def test_write_mode_produces_files() -> None:
    """Write mode creates tracker and derived data files."""
    fs = _make_fs()
    _, code = run_generate_pipeline(
        fs, _make_git(), CONFIG, write=True, existing_tracker=None,
    )
    assert code == 0
    assert "tracker.json" in fs.files
    assert "derived.json" in fs.files


def test_report_contains_expected_sections() -> None:
    """Report contains all expected section headers."""
    fs = _make_fs()
    report, _ = run_generate_pipeline(
        fs, _make_git(), CONFIG, write=False, existing_tracker=None,
    )
    plain = click.unstyle(report)
    for section in [
        "Dependency Cycles", "Orphan Packages",
        "depended_on_by Consistency", "Warning Flags",
        "High-Risk Flags", "Multi-Package Init Files",
        "New Dependencies", "Upgrade Order", "Validation",
    ]:
        assert section in plain, f"Missing section: {section}"
