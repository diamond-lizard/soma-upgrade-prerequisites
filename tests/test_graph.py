#!/usr/bin/env python3
# Tests for dependency graph construction functions.
from __future__ import annotations

from soma_upgrade_prerequisites.graph import (
    build_init_file_dep_graph,
    build_package_to_init_mapping,
)
from soma_upgrade_prerequisites.models import DependencyGraph


def test_build_package_to_init_mapping() -> None:
    """Each package maps to its declaring init file."""
    graph = DependencyGraph.model_validate({
        "soma-magit-init.el": {
            "packages": [
                {
                    "package": "magit",
                    "depends_on": [],
                    "repo_url": "https://example.com",
                    "min_emacs_version": None,
                },
            ],
            "depended_on_by": [],
        },
        "soma-forge-init.el": {
            "packages": [
                {
                    "package": "forge",
                    "depends_on": ["magit"],
                    "repo_url": "https://example.com",
                    "min_emacs_version": None,
                },
            ],
            "depended_on_by": [],
        },
    })
    result = build_package_to_init_mapping(graph)
    assert result == {
        "magit": "soma-magit-init.el",
        "forge": "soma-forge-init.el",
    }


def test_build_init_file_dep_graph() -> None:
    """Package deps resolve to init-file deps via pkg_to_init."""
    graph = DependencyGraph.model_validate({
        "soma-magit-init.el": {
            "packages": [
                {
                    "package": "magit",
                    "depends_on": [],
                    "repo_url": "https://example.com",
                    "min_emacs_version": None,
                },
            ],
            "depended_on_by": [],
        },
        "soma-forge-init.el": {
            "packages": [
                {
                    "package": "forge",
                    "depends_on": ["magit"],
                    "repo_url": "https://example.com",
                    "min_emacs_version": None,
                },
            ],
            "depended_on_by": [],
        },
    })
    pkg_to_init = {"magit": "soma-magit-init.el", "forge": "soma-forge-init.el"}
    result = build_init_file_dep_graph(graph, pkg_to_init)
    assert result == {
        "soma-magit-init.el": [],
        "soma-forge-init.el": ["soma-magit-init.el"],
    }
