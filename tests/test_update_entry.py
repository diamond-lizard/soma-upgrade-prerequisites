#!/usr/bin/env python3
# Tests for update_entry function.
from __future__ import annotations

import pytest

from soma_upgrade_prerequisites.tracker_update import update_entry
from tests.tracker_test_helpers import make_entry, make_tracker


def test_changes_status() -> None:
    """update_entry changes an entry's status."""
    t = make_tracker([make_entry()])
    result = update_entry(t, "a.el", "in-progress", None, False)
    assert result.entries[0].status == "in-progress"


def test_sets_note() -> None:
    """update_entry sets the note when provided."""
    t = make_tracker([make_entry()])
    result = update_entry(t, "a.el", "pending", "a note", False)
    assert result.entries[0].notes == "a note"


def test_preserves_note_when_none() -> None:
    """update_entry preserves existing note when note is None."""
    t = make_tracker([make_entry(notes="old")])
    result = update_entry(t, "a.el", "pending", None, False)
    assert result.entries[0].notes == "old"


def test_unknown_init_file_raises() -> None:
    """update_entry raises ValueError for unknown init files."""
    t = make_tracker([make_entry()])
    with pytest.raises(ValueError, match="not found"):
        update_entry(t, "missing.el", "pending", None, False)


def test_terminal_to_nonterminal_without_force_raises() -> None:
    """Changing terminal status without force raises ValueError."""
    t = make_tracker([make_entry(status="upgraded")])
    with pytest.raises(ValueError, match="force"):
        update_entry(t, "a.el", "pending", None, False)


def test_terminal_to_nonterminal_with_force_ok() -> None:
    """Force allows changing terminal to non-terminal."""
    t = make_tracker([make_entry(status="upgraded")])
    result = update_entry(t, "a.el", "pending", None, True)
    assert result.entries[0].status == "pending"


def test_replaces_blocked_by_when_provided() -> None:
    """update_entry replaces blocked_by when given."""
    t = make_tracker([make_entry()])
    result = update_entry(
        t, "a.el", "blocked", None, False, blocked_by=["b.el"],
    )
    assert result.entries[0].blocked_by == ["b.el"]


def test_preserves_blocked_by_when_none() -> None:
    """update_entry preserves blocked_by when not provided."""
    t = make_tracker([make_entry(blocked_by=["x.el"])])
    result = update_entry(t, "a.el", "pending", None, False)
    assert result.entries[0].blocked_by == ["x.el"]


def test_immutability() -> None:
    """Original tracker is unchanged after update_entry."""
    t = make_tracker([make_entry()])
    update_entry(t, "a.el", "in-progress", "note", False)
    assert t.entries[0].status == "pending"
    assert t.entries[0].notes == ""
