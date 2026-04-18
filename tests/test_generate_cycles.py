#!/usr/bin/env python3
# Integration test for dependency cycle detection in the pipeline.
from __future__ import annotations

import json

import click

from soma_upgrade_prerequisites.config import PipelineConfig
from soma_upgrade_prerequisites.pipeline import run_generate_pipeline
from tests.fake_git import FakeGitClient
from tests.fakes import InMemoryFileSystem
from tests.helpers import pkg

CONFIG = PipelineConfig(
    graph_json_path="graph.json",
    upgrades_dir="upgrades",
    inits_dir="inits",
    branch="elpaca-upgrades",
    tracker_path="tracker.json",
    derived_data_path="derived.json",
)


def test_cycles_produce_fail() -> None:
    """Exit code 1 when dependency cycles exist."""
    graph = {
        "soma-a-init.el": {
            "packages": [pkg("a", ["b"])],
            "depended_on_by": ["soma-b-init.el"],
        },
        "soma-b-init.el": {
            "packages": [pkg("b", ["a"])],
            "depended_on_by": ["soma-a-init.el"],
        },
    }
    fs = InMemoryFileSystem({
        "graph.json": json.dumps(graph),
        "upgrades/soma-a-init.el-upgrade-process.md": "# U\n",
        "upgrades/soma-b-init.el-upgrade-process.md": "# U\n",
        "upgrades/soma-a-init.el-security-review.md": "# S\n",
        "upgrades/soma-b-init.el-security-review.md": "# S\n",
    })
    git = FakeGitClient("abc", [], "elpaca-upgrades")
    report, code = run_generate_pipeline(
        fs, git, CONFIG, write=False, existing_tracker=None,
    )
    assert code == 1
    plain = click.unstyle(report)
    assert "Dependency Cycles" in plain
    assert "FAIL" in plain
