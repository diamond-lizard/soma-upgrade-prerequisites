#!/usr/bin/env python3
# Tests for the update-note subcommand.
from __future__ import annotations

from click.testing import CliRunner

from soma_upgrade_prerequisites.main import cli
from soma_upgrade_prerequisites.tracker_update import update_entry

from .tracker_test_helpers import make_entry, make_tracker


def test_update_note_help() -> None:
    """(a) update-note --help prints help text."""
    runner = CliRunner()
    result = runner.invoke(cli, ["update-note", "--help"])
    assert result.exit_code == 0
    assert "update-note" in result.output.lower()


def test_update_note_missing_note_flag() -> None:
    """(b) Missing --note flag produces an error."""
    runner = CliRunner()
    result = runner.invoke(cli, ["update-note", "a.el"])
    assert result.exit_code != 0


def test_update_note_missing_tracker(tmp_path: object) -> None:
    """(c) Missing tracker file produces exit code 1."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "update-note", "a.el",
        "--note", "test note",
        "--tracker", "/nonexistent/tracker.json",
    ])
    assert result.exit_code == 1


def test_update_note_changes_note() -> None:
    """(d) Note is updated on the specified entry."""
    tracker = make_tracker([make_entry("a.el", notes="old")])
    updated = update_entry(
        tracker, "a.el", "pending", note="new note", force=False,
    )
    entry = next(e for e in updated.entries if e.init_file == "a.el")
    assert entry.notes == "new note"


def test_update_note_preserves_status_and_blocked_by() -> None:
    """(e) Status and blocked_by are unchanged after note update."""
    tracker = make_tracker([
        make_entry("a.el", status="blocked", blocked_by=["x.el"]),
    ])
    updated = update_entry(
        tracker, "a.el", "blocked", note="new", force=False,
    )
    entry = next(e for e in updated.entries if e.init_file == "a.el")
    assert entry.status == "blocked"
    assert entry.blocked_by == ["x.el"]


def test_update_note_unknown_init_file() -> None:
    """(f) Unknown init file raises ValueError."""
    tracker = make_tracker([make_entry("a.el")])
    try:
        update_entry(
            tracker, "unknown.el", "pending",
            note="note", force=False,
        )
        raised = False
    except ValueError:
        raised = True
    assert raised
