#!/usr/bin/env python3
"""Orphan package detection and classification."""
# Orphan package detection and classification.
# Identifies packages in depends_on that have no declaring init file.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .models import DependencyGraph, OrphanPackage
    from .protocols import FileSystem

from .orphan_classify import classify_orphan


def find_orphan_packages(
    graph_data: DependencyGraph,
    pkg_to_init: Mapping[str, str],
    fs: FileSystem,
    inits_dir: str,
    upgrades_dir: str,
) -> list[OrphanPackage]:
    """Find packages in depends_on with no entry in pkg_to_init.

    Classifies each as misidentified, dependency-not-to-be-upgraded,
    missing-from-multi-package, or unresolvable.
    """
    all_deps = _collect_all_deps(graph_data)
    orphan_names = sorted(all_deps - set(pkg_to_init))
    return [
        classify_orphan(name, graph_data, fs, inits_dir, upgrades_dir)
        for name in orphan_names
    ]


def _collect_all_deps(graph_data: DependencyGraph) -> set[str]:
    """Collect all package names referenced in depends_on lists."""
    return {
        dep
        for _, entry in graph_data.items()
        for pkg in entry.packages
        for dep in pkg.depends_on
    }


