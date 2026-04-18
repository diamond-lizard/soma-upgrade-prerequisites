#!/usr/bin/env python3
# Tests for graph validation functions.
from __future__ import annotations

from soma_upgrade_prerequisites.graph import validate_depended_on_by
from soma_upgrade_prerequisites.models import DependencyGraph


def test_validate_depended_on_by_consistent() -> None:
    """Returns empty list when depended_on_by matches reverse deps."""
    graph = DependencyGraph.model_validate({
        "a.el": {
            "packages": [{"package": "a", "depends_on": [],
                          "repo_url": "", "min_emacs_version": None}],
            "depended_on_by": ["b.el"],
        },
        "b.el": {
            "packages": [{"package": "b", "depends_on": ["a"],
                          "repo_url": "", "min_emacs_version": None}],
            "depended_on_by": [],
        },
    })
    reverse = {"a.el": ["b.el"], "b.el": []}
    assert validate_depended_on_by(graph, reverse) == []


def test_validate_depended_on_by_discrepancy() -> None:
    """Returns error messages when depended_on_by is inconsistent."""
    graph = DependencyGraph.model_validate({
        "a.el": {
            "packages": [{"package": "a", "depends_on": [],
                          "repo_url": "", "min_emacs_version": None}],
            "depended_on_by": [],
        },
        "b.el": {
            "packages": [{"package": "b", "depends_on": ["a"],
                          "repo_url": "", "min_emacs_version": None}],
            "depended_on_by": [],
        },
    })
    reverse = {"a.el": ["b.el"], "b.el": []}
    errors = validate_depended_on_by(graph, reverse)
    assert len(errors) > 0
