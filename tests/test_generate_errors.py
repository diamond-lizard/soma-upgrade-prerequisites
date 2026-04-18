#!/usr/bin/env python3
# Integration tests for pipeline error conditions.
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


def test_missing_graph_json() -> None:
    """Exit code 1 when graph JSON not found."""
    fs = InMemoryFileSystem()
    git = FakeGitClient("abc", [], "elpaca-upgrades")
    _, code = run_generate_pipeline(
        fs, git, CONFIG, write=False, existing_tracker=None,
    )
    assert code == 1


def test_git_error() -> None:
    """Exit code 1 when git commit hash fails."""
    fs = InMemoryFileSystem({"graph.json": json.dumps({})})
    git = FakeGitClient("x", [], "elpaca-upgrades", commit_hash_error="fail")
    _, code = run_generate_pipeline(
        fs, git, CONFIG, write=False, existing_tracker=None,
    )
    assert code == 1


def test_malformed_graph_json() -> None:
    """Exit code 1 when graph JSON is malformed."""
    fs = InMemoryFileSystem({"graph.json": "not json"})
    git = FakeGitClient("abc", [], "elpaca-upgrades")
    _, code = run_generate_pipeline(
        fs, git, CONFIG, write=False, existing_tracker=None,
    )
    assert code == 1


def test_missing_security_reviews() -> None:
    """Exit code 1 when security reviews are missing."""
    graph = {
        "soma-a-init.el": {
            "packages": [pkg("a")],
            "depended_on_by": [],
        },
    }
    fs = InMemoryFileSystem({
        "graph.json": json.dumps(graph),
        "upgrades/soma-a-init.el-upgrade-process.md": "# Upgrade\n",
    })
    git = FakeGitClient("abc", [], "elpaca-upgrades")
    report, code = run_generate_pipeline(
        fs, git, CONFIG, write=False, existing_tracker=None,
    )
    assert code == 1
    assert "Missing Security Reviews" in click.unstyle(report)


def test_uncovered_upgrade_set() -> None:
    """Exit code 1 when upgrade set has init files not in graph."""
    fs = InMemoryFileSystem({
        "graph.json": json.dumps({}),
        "upgrades/soma-x-init.el-upgrade-process.md": "",
    })
    git = FakeGitClient("abc", [], "elpaca-upgrades")
    report, code = run_generate_pipeline(
        fs, git, CONFIG, write=False, existing_tracker=None,
    )
    assert code == 1
    assert "Coverage" in click.unstyle(report)
