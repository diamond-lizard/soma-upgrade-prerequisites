#!/usr/bin/env python3
# Tests for compute_critical_path.
from __future__ import annotations

from soma_upgrade_prerequisites.critical_path import compute_critical_path


def test_critical_path_longest_chain() -> None:
    """Returns the longest dependency chain from root to leaf."""
    graph = {"a.el": ["b.el"], "b.el": ["c.el"], "c.el": []}
    path = compute_critical_path(graph, ["a.el", "b.el", "c.el"])
    assert path == ["c.el", "b.el", "a.el"]


def test_critical_path_tiebreak_deterministic() -> None:
    """Equal-length chains produce a deterministic result."""
    graph = {
        "a.el": ["c.el"], "b.el": ["c.el"], "c.el": [],
    }
    path = compute_critical_path(graph, ["a.el", "b.el", "c.el"])
    assert len(path) == 2
    assert path[0] == "c.el"
