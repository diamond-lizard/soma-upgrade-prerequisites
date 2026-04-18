#!/usr/bin/env python3
# Tests for validation check functions.
from __future__ import annotations

from soma_upgrade_prerequisites.validation import (
    validate_mapping_completeness,
    validate_reverse_deps,
    validate_topological_order,
)
from tests.helpers import make_graph, pkg


def test_mapping_complete() -> None:
    """Returns empty list when all packages are mapped."""
    graph = make_graph({
        "a.el": {"packages": [pkg("x")], "depended_on_by": []},
    })
    assert validate_mapping_completeness(graph, {"x": "a.el"}) == []


def test_mapping_missing_package() -> None:
    """Returns errors when packages are missing from the mapping."""
    graph = make_graph({
        "a.el": {"packages": [pkg("x")], "depended_on_by": []},
    })
    errors = validate_mapping_completeness(graph, {})
    assert len(errors) == 1
    assert "x" in errors[0]


def test_topological_order_valid() -> None:
    """Returns empty list when deps appear before dependents."""
    sorted_files = ["b.el", "a.el"]
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    assert validate_topological_order(sorted_files, dep_graph) == []


def test_topological_order_invalid() -> None:
    """Returns errors when a dependency appears after its dependent."""
    sorted_files = ["a.el", "b.el"]
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    errors = validate_topological_order(sorted_files, dep_graph)
    assert len(errors) == 1
    assert "b.el" in errors[0]


def test_reverse_deps_consistent() -> None:
    """Returns empty list when reverse deps are consistent."""
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    reverse = {"a.el": [], "b.el": ["a.el"]}
    assert validate_reverse_deps(dep_graph, reverse) == []


def test_reverse_deps_inconsistent() -> None:
    """Returns errors when A depends on B but B's reverse deps miss A."""
    dep_graph = {"a.el": ["b.el"], "b.el": []}
    reverse = {"a.el": [], "b.el": []}
    errors = validate_reverse_deps(dep_graph, reverse)
    assert len(errors) == 1
    assert "a.el" in errors[0]
