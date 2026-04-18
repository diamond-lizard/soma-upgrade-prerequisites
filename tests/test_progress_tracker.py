#!/usr/bin/env python3
# Tests for progress tracker create, read, update, and write.
from __future__ import annotations

from soma_upgrade_prerequisites.progress_tracker import create_tracker
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
