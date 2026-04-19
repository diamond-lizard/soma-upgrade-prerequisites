#!/usr/bin/env python3
# Tests for the show-tracker subcommand.
from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from soma_upgrade_prerequisites.main import cli
from soma_upgrade_prerequisites.report_table import format_table

from .tracker_test_helpers import make_entry, make_tracker


def test_show_help() -> None:
    """(a) show --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["show-tracker", "--help"])
    assert result.exit_code == 0
    assert "show-tracker" in result.output.lower()


def test_show_invalid_status() -> None:
    """(b) Invalid --status value is handled."""
    runner = CliRunner()
    result = runner.invoke(cli, ["show-tracker", "--status", "nonsense"])
    assert result.exit_code != 0


def test_show_format_table_output() -> None:
    """(c) Formatted output from a valid tracker."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="upgraded"),
    ])
    output = format_table(tracker, status_filter=None, flags_only=False)
    assert "a.el" in output
    assert "b.el" in output


def test_show_status_filter() -> None:
    """(d) --status pending filters to only pending entries."""
    tracker = make_tracker([
        make_entry("a.el", status="pending"),
        make_entry("b.el", status="upgraded"),
    ])
    output = format_table(tracker, status_filter="pending", flags_only=False)
    assert "a.el" in output
    assert "b.el" not in output


def test_show_flags_filter() -> None:
    """(e) --flags filters to only flagged entries."""
    tracker = make_tracker([
        make_entry("a.el", status="pending", flags=["warned"]),
        make_entry("b.el", status="pending"),
    ])
    output = format_table(tracker, status_filter=None, flags_only=True)
    assert "a.el" in output
    assert "b.el" not in output


def test_show_missing_tracker() -> None:
    """(f) Missing tracker file causes exit code 1."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--tracker", "/nonexistent/tracker.json",
    ])
    assert result.exit_code == 1
    assert "write-analysis" in result.output


def _write_test_files(
    tmp: Path, tracker_entries: list[object],
    reverse_deps: dict[str, list[str]],
) -> tuple[str, str, str]:
    """Write tracker, derived data, and graph files. Return paths."""
    tracker = make_tracker(tracker_entries)
    tracker_path = str(tmp / "tracker.json")
    Path(tracker_path).write_text(tracker.model_dump_json(indent=2))
    import hashlib
    graph_content = "{}"
    graph_path = str(tmp / "graph.json")
    Path(graph_path).write_text(graph_content)
    graph_hash = hashlib.sha256(graph_content.encode()).hexdigest()
    derived = {
        "schema_version": 1,
        "source_graph_hash": graph_hash,
        "pkg_to_init": {}, "init_to_packages": {},
        "init_dep_graph": {}, "sorted_files": [],
        "reverse_deps": reverse_deps,
    }
    dd_path = str(tmp / "derived.json")
    Path(dd_path).write_text(json.dumps(derived))
    return tracker_path, dd_path, graph_path


def test_show_dependents_with_candidates(tmp_path: Path) -> None:
    """(g) --dependents shows cascade candidates."""
    tp, dd, gp = _write_test_files(tmp_path, [
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="pending"),
    ], {"a.el": ["b.el"]})
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--dependents", "a.el",
        "--tracker", tp, "--derived-data", dd, "--graph-json", gp,
    ])
    assert result.exit_code == 0
    assert "b.el" in result.output


def test_show_dependents_missing_derived(tmp_path: Path) -> None:
    """(h) --dependents with missing derived data exits 1."""
    tracker = make_tracker([make_entry("a.el")])
    tp = str(tmp_path / "tracker.json")
    Path(tp).write_text(tracker.model_dump_json(indent=2))
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--dependents", "a.el",
        "--tracker", tp, "--derived-data", "/nonexistent/dd.json",
        "--graph-json", "/nonexistent/g.json",
    ])
    assert result.exit_code == 1
    assert "write-analysis" in result.output


def test_show_dependents_stale_data(tmp_path: Path) -> None:
    """(i) --dependents with stale hash exits 1."""
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
        "show-tracker", "--dependents", "a.el",
        "--tracker", tp, "--derived-data", dd, "--graph-json", gp,
    ])
    assert result.exit_code == 1


def test_show_dependents_unknown_init(tmp_path: Path) -> None:
    """(j) --dependents with unknown init file exits 1."""
    tp, dd, gp = _write_test_files(tmp_path, [
        make_entry("a.el"),
    ], {})
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--dependents", "unknown.el",
        "--tracker", tp, "--derived-data", dd, "--graph-json", gp,
    ])
    assert result.exit_code == 1


def test_show_dependents_no_dependents(tmp_path: Path) -> None:
    """(k) --dependents with no dependents shows message."""
    tp, dd, gp = _write_test_files(tmp_path, [
        make_entry("a.el"),
    ], {})
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--dependents", "a.el",
        "--tracker", tp, "--derived-data", dd, "--graph-json", gp,
    ])
    assert result.exit_code == 0
    assert "no dependents" in result.output.lower()


def test_show_dependents_mixed_sections(tmp_path: Path) -> None:
    """(l) Both cascade candidates and other dependents shown."""
    tp, dd, gp = _write_test_files(tmp_path, [
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="pending"),
        make_entry("c.el", status="upgraded"),
    ], {"a.el": ["b.el", "c.el"]})
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--dependents", "a.el",
        "--tracker", tp, "--derived-data", dd, "--graph-json", gp,
    ])
    assert result.exit_code == 0
    assert "b.el" in result.output
    assert "c.el" in result.output
    assert "other dependents" in result.output.lower()


def test_show_dependents_all_terminal(tmp_path: Path) -> None:
    """(m) All terminal dependents: no cascade section, only other."""
    tp, dd, gp = _write_test_files(tmp_path, [
        make_entry("a.el", status="skipped"),
        make_entry("b.el", status="upgraded"),
        make_entry("c.el", status="reverted"),
    ], {"a.el": ["b.el", "c.el"]})
    runner = CliRunner()
    result = runner.invoke(cli, [
        "show-tracker", "--dependents", "a.el",
        "--tracker", tp, "--derived-data", dd, "--graph-json", gp,
    ])
    assert result.exit_code == 0
    assert "cascade candidates" not in result.output.lower()
    assert "other dependents" in result.output.lower()
