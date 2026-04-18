#!/usr/bin/env python3
# Tests for progress tracker create, read, update, and write.
from __future__ import annotations

import pytest
from pydantic import ValidationError

from soma_upgrade_prerequisites.progress_tracker import (
    create_tracker,
    find_direct_dependents_any_status,
    read_tracker,
)
from tests.fakes import InMemoryFileSystem
from tests.helpers import make_graph, pkg


def test_create_tracker() -> None:
    """create_tracker produces valid entries with correct fields."""
    graph = make_graph({
        "a.el": {
            "packages": [pkg("pkg-a")],
            "depended_on_by": [],
        },
        "b.el": {
            "packages": [pkg("pkg-b", ["pkg-a"])],
            "depended_on_by": [],
        },
    })
    levels = {"a.el": 0, "b.el": 1}
    flags: dict[str, list[str]] = {"b.el": ["warned"]}
    tracker = create_tracker(
        "abc123", ["a.el", "b.el"], graph, levels, flags,
    )
    assert tracker.schema_version == 1
    assert tracker.starting_commit == "abc123"
    assert len(tracker.entries) == 2

    e0 = tracker.entries[0]
    assert e0.order == 1
    assert e0.init_file == "a.el"
    assert e0.package == "pkg-a"
    assert e0.level == 0
    assert e0.flags == []
    assert e0.status == "pending"
    assert e0.notes == ""
    assert e0.blocked_by == []

    e1 = tracker.entries[1]
    assert e1.order == 2
    assert e1.init_file == "b.el"
    assert e1.flags == ["warned"]


def test_read_tracker_missing_file() -> None:
    """read_tracker returns None for a non-existent file."""
    fs = InMemoryFileSystem()
    assert read_tracker(fs, "missing.json") is None


def test_read_tracker_malformed_json() -> None:
    """read_tracker raises ValidationError on malformed JSON."""
    fs = InMemoryFileSystem({"t.json": "not json"})
    with pytest.raises(ValidationError):
        read_tracker(fs, "t.json")


def test_read_tracker_version_mismatch() -> None:
    """read_tracker raises ValueError on schema version mismatch."""
    bad_tracker = (
        '{"schema_version": 999, "starting_commit": "x",'
        ' "generated_at": "t", "status_definitions": {},'
        ' "entries": []}'
    )
    fs = InMemoryFileSystem({"t.json": bad_tracker})
    with pytest.raises(ValueError, match=r"re-run"):
        read_tracker(fs, "t.json")


def test_find_direct_dependents_any_status() -> None:
    """Returns all tracker entries that directly depend on the given file."""
    from tests.tracker_test_helpers import make_entry, make_tracker

    tracker = make_tracker([
        make_entry("a.el"),
        make_entry("b.el", "upgraded"),
        make_entry("c.el", "blocked"),
    ])
    reverse_deps = {"a.el": ["b.el", "c.el"], "b.el": [], "c.el": []}
    result = find_direct_dependents_any_status(
        "a.el", reverse_deps, tracker,
    )
    assert sorted(result) == ["b.el", "c.el"]
