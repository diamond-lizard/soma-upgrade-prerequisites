#!/usr/bin/env python3
"""Dependency graph construction functions."""
# Dependency graph construction functions.
# Builds mappings, init-file dependency graphs, and reverse dependencies.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .models import DependencyGraph


def build_package_to_init_mapping(
    graph_data: DependencyGraph,
) -> dict[str, str]:
    """Map each package name to the init file that declares it."""
    return {
        pkg.package: init_file
        for init_file, entry in graph_data.items()
        for pkg in entry.packages
    }


def build_init_file_dep_graph(
    graph_data: DependencyGraph,
    pkg_to_init: Mapping[str, str],
) -> dict[str, list[str]]:
    """Build init-file-to-init-file dependency graph.

    Resolves package dependencies through pkg_to_init mapping.
    Skips self-dependencies and unmapped packages.
    """
    result: dict[str, list[str]] = {}
    for init_file, entry in graph_data.items():
        deps: list[str] = []
        for pkg in entry.packages:
            for dep_pkg in pkg.depends_on:
                dep_init = pkg_to_init.get(dep_pkg)
                if dep_init is not None and dep_init != init_file:
                    deps.append(dep_init)
        result[init_file] = sorted(set(deps))
    return result


def build_reverse_deps(
    init_dep_graph: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    """Compute direct reverse dependencies (one hop).

    For each init file, which other init files directly depend on it.
    """
    result: dict[str, list[str]] = {k: [] for k in init_dep_graph}
    for init_file, deps in init_dep_graph.items():
        for dep in deps:
            if dep in result:
                result[dep].append(init_file)
    return result


def validate_depended_on_by(
    graph_data: DependencyGraph,
    reverse_deps: Mapping[str, Sequence[str]],
) -> list[str]:
    """Cross-check JSON depended_on_by against computed reverse deps.

    Returns a list of discrepancy messages (empty means consistent).
    """
    errors: list[str] = []
    for name, entry in graph_data.items():
        declared = sorted(entry.depended_on_by)
        computed = sorted(reverse_deps.get(name, []))
        if declared != computed:
            errors.append(
                f"{name}: depended_on_by {declared} != computed {computed}"
            )
    return errors
