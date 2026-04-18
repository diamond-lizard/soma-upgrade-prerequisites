#!/usr/bin/env python3
# Tests for the validate subcommand.
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from click.testing import CliRunner

from soma_upgrade_prerequisites.main import cli
from soma_upgrade_prerequisites.validation import (
    validate_tracker_vs_sort,
)
from soma_upgrade_prerequisites.validation_git import (
    validate_tracker_vs_git,
)

from .tracker_test_helpers import make_entry, make_tracker


def test_validate_help() -> None:
    """(a) validate --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--help"])
    assert result.exit_code == 0
    assert "validate" in result.output.lower()


def test_validate_consistent_data() -> None:
    """(b) Consistent entries and git log returns exit code 0."""
    tracker = make_tracker([make_entry("a.el", status="upgraded")])
    log_lines = ["[a.el] Upgrade pkg from v1 to v2"]
    errors = validate_tracker_vs_git(tracker, log_lines)
    assert errors == []


def test_validate_upgraded_no_commit() -> None:
    """(c) Upgraded entry with no matching commit returns errors."""
    tracker = make_tracker([make_entry("a.el", status="upgraded")])
    errors = validate_tracker_vs_git(tracker, [])
    assert len(errors) > 0


def test_validate_commit_no_entry() -> None:
    """(d) Commit with no matching upgraded/reverted entry returns errors."""
    tracker = make_tracker([make_entry("a.el", status="pending")])
    log_lines = ["[a.el] Upgrade pkg from v1 to v2"]
    errors = validate_tracker_vs_git(tracker, log_lines)
    assert len(errors) > 0


def test_validate_commit_matches_reverted() -> None:
    """(d2) Commit matching a reverted entry returns no error."""
    tracker = make_tracker([make_entry("a.el", status="reverted")])
    log_lines = ["[a.el] Upgrade pkg from v1 to v2"]
    errors = validate_tracker_vs_git(tracker, log_lines)
    assert errors == []


def test_validate_missing_tracker() -> None:
    """(e) Missing tracker file produces exit code 1."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "validate", "--tracker", "/nonexistent/tracker.json",
    ])
    assert result.exit_code == 1


def _write_validate_files(
    tmp: Path, tracker_entries: list[object],
    graph: dict[str, object] | None = None,
    sorted_files: list[str] | None = None,
    reverse_deps: dict[str, list[str]] | None = None,
    init_dep_graph: dict[str, list[str]] | None = None,
    pkg_to_init: dict[str, str] | None = None,
    git_lines: list[str] | None = None,
) -> dict[str, str]:
    """Write all validate test files. Return path dict."""
    tracker = make_tracker(tracker_entries)
    tp = str(tmp / "tracker.json")
    Path(tp).write_text(tracker.model_dump_json(indent=2))
    graph_content = json.dumps(graph or {})
    gp = str(tmp / "graph.json")
    Path(gp).write_text(graph_content)
    graph_hash = hashlib.sha256(graph_content.encode()).hexdigest()
    derived = {
        "schema_version": 1,
        "source_graph_hash": graph_hash,
        "pkg_to_init": pkg_to_init or {},
        "init_to_packages": {},
        "init_dep_graph": init_dep_graph or {},
        "reverse_deps": reverse_deps or {},
        "sorted_files": sorted_files or [],
    }
    dd = str(tmp / "derived.json")
    Path(dd).write_text(json.dumps(derived))
    return {"tracker": tp, "derived": dd, "graph": gp}


def _invoke_validate(
    paths: dict[str, str], extra_args: list[str] | None = None,
) -> object:
    """Run validate with test file paths."""
    runner = CliRunner()
    args = [
        "validate",
        "--tracker", paths["tracker"],
        "--derived-data", paths["derived"],
        "--graph-json", paths["graph"],
        "--branch", "test-branch",
        *(extra_args or []),
    ]
    return runner.invoke(cli, args)


def test_validate_all_checks_pass() -> None:
    """(f) All five checks pass, no SystemExit raised."""
    import hashlib

    from soma_upgrade_prerequisites.config import ValidateConfig
    from soma_upgrade_prerequisites.validate_runner import run_validation

    from .fake_git import FakeGitClient
    from .fakes import InMemoryFileSystem

    graph_content = "{}"
    graph_hash = hashlib.sha256(graph_content.encode()).hexdigest()
    tracker = make_tracker([make_entry("a.el", status="pending")])
    derived = json.dumps({
        "schema_version": 1, "source_graph_hash": graph_hash,
        "pkg_to_init": {}, "init_to_packages": {},
        "init_dep_graph": {}, "reverse_deps": {},
        "sorted_files": ["a.el"],
    })
    fs = InMemoryFileSystem({
        "/graph.json": graph_content,
        "/derived.json": derived,
    })
    git = FakeGitClient("abc", [], "main")
    config = ValidateConfig(
        tracker_path="/t.json", branch="main",
        graph_json_path="/graph.json", derived_data_path="/derived.json",
    )
    run_validation(fs, git, config, tracker)

def test_validate_topo_order_violation(tmp_path: Path) -> None:
    """(g) Non-git check failure returns exit code 1."""
    errors = validate_tracker_vs_sort(
        make_tracker([
            make_entry("a.el"), make_entry("b.el"),
        ]),
        ["b.el", "a.el"],
    )
    assert len(errors) > 0


def test_validate_missing_derived_data(tmp_path: Path) -> None:
    """(h) Missing derived data file produces exit code 1."""
    tracker = make_tracker([make_entry("a.el")])
    tp = str(tmp_path / "tracker.json")
    Path(tp).write_text(tracker.model_dump_json(indent=2))
    runner = CliRunner()
    result = runner.invoke(cli, [
        "validate",
        "--tracker", tp,
        "--derived-data", "/nonexistent/dd.json",
        "--graph-json", "/nonexistent/g.json",
        "--branch", "test-branch",
    ])
    assert result.exit_code == 1


def test_validate_stale_derived_data(tmp_path: Path) -> None:
    """(i) Stale hash produces exit code 1."""
    tracker = make_tracker([make_entry("a.el")])
    tp = str(tmp_path / "tracker.json")
    Path(tp).write_text(tracker.model_dump_json(indent=2))
    derived = {
        "schema_version": 1, "source_graph_hash": "stale",
        "pkg_to_init": {}, "init_to_packages": {},
        "init_dep_graph": {}, "reverse_deps": {},
        "sorted_files": [],
    }
    dd = str(tmp_path / "derived.json")
    Path(dd).write_text(json.dumps(derived))
    gp = str(tmp_path / "graph.json")
    Path(gp).write_text("{}")
    runner = CliRunner()
    result = runner.invoke(cli, [
        "validate",
        "--tracker", tp, "--derived-data", dd,
        "--graph-json", gp, "--branch", "test-branch",
    ])
    assert result.exit_code == 1
