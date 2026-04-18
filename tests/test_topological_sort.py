#!/usr/bin/env python3
# Tests for topological sort, dependency levels, and critical path.
from __future__ import annotations

from soma_upgrade_prerequisites.topological_sort import (
    assign_dependency_levels,
    compute_topological_sort,
)


def test_elpaca_first_when_in_upgrade_set() -> None:
    """Elpaca init file appears first in the sort."""
    graph = {"init.el": [], "a.el": [], "b.el": []}
    upgrade = ["a.el", "init.el", "b.el"]
    result = compute_topological_sort(
        graph, upgrade, [], {}, "init.el",
    )
    assert result[0] == "init.el"


def test_dependencies_before_dependents() -> None:
    """Dependencies always appear before their dependents."""
    graph = {"a.el": ["b.el"], "b.el": []}
    upgrade = ["a.el", "b.el"]
    result = compute_topological_sort(
        graph, upgrade, [], {"a.el": [], "b.el": ["a.el"]}, "init.el",
    )
    assert result.index("b.el") < result.index("a.el")


def test_warned_files_early() -> None:
    """Warned files appear as early as deps allow."""
    graph = {"a.el": [], "b.el": [], "c.el": []}
    reverse = {"a.el": [], "b.el": [], "c.el": []}
    result = compute_topological_sort(
        graph, ["a.el", "b.el", "c.el"], ["c.el"], reverse, "init.el",
    )
    assert result[0] == "c.el"


def test_more_dependents_first_at_same_level() -> None:
    """At the same level, files with more dependents come first."""
    graph = {"a.el": [], "b.el": []}
    reverse = {"a.el": ["x", "y", "z"], "b.el": ["x"]}
    result = compute_topological_sort(
        graph, ["a.el", "b.el"], [], reverse, "init.el",
    )
    assert result.index("a.el") < result.index("b.el")


def test_warned_beats_more_dependents() -> None:
    """Rule 3 (warned) takes precedence over rule 4 (dependents)."""
    graph = {"a.el": [], "b.el": []}
    reverse = {"a.el": ["x", "y", "z"], "b.el": []}
    result = compute_topological_sort(
        graph, ["a.el", "b.el"], ["b.el"], reverse, "init.el",
    )
    assert result[0] == "b.el"


def test_level_zero_for_root_nodes() -> None:
    """Root nodes with no upgrade-set deps get level 0."""
    graph = {"a.el": [], "b.el": ["a.el"]}
    levels = assign_dependency_levels(graph, ["a.el", "b.el"])
    assert levels["a.el"] == 0


def test_level_one_for_direct_deps() -> None:
    """Nodes whose upgrade-set deps are all level 0 get level 1."""
    graph = {"a.el": [], "b.el": ["a.el"]}
    levels = assign_dependency_levels(graph, ["a.el", "b.el"])
    assert levels["b.el"] == 1


def test_single_node_level_zero() -> None:
    """A single-node graph returns level 0."""
    graph = {"a.el": []}
    levels = assign_dependency_levels(graph, ["a.el"])
    assert levels["a.el"] == 0


def test_transitive_through_non_upgrade_nodes() -> None:
    """Transitive deps through non-upgrade nodes are respected."""
    graph = {"a.el": ["x.el"], "x.el": ["b.el"], "b.el": []}
    levels = assign_dependency_levels(graph, ["a.el", "b.el"])
    assert levels["b.el"] == 0
    assert levels["a.el"] >= 1
