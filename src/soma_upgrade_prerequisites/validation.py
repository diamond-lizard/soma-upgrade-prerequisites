#!/usr/bin/env python3
# Validation checks for dependency data consistency.
# Pure functions that return lists of error messages.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .models import DependencyGraph


def validate_mapping_completeness(
    graph_data: DependencyGraph,
    pkg_to_init: Mapping[str, str],
) -> list[str]:
    """Verify every package in the graph has an entry in the mapping.

    Returns a list of error messages (empty means valid).
    """
    errors: list[str] = []
    for name, entry in graph_data.items():
        for p in entry.packages:
            if p.package not in pkg_to_init:
                errors.append(
                    f"Package '{p.package}' in {name} has no mapping"
                )
    return errors


def validate_topological_order(
    sorted_files: Sequence[str],
    dep_graph: Mapping[str, Sequence[str]],
) -> list[str]:
    """Verify every init file's deps appear earlier in the sort.

    Returns a list of error messages (empty means valid).
    """
    position = {f: i for i, f in enumerate(sorted_files)}
    errors: list[str] = []
    for init_file in sorted_files:
        for dep in dep_graph.get(init_file, []):
            if dep in position and position[dep] > position[init_file]:
                errors.append(
                    f"{dep} appears after {init_file} but is a dependency"
                )
    return errors


def validate_reverse_deps(
    dep_graph: Mapping[str, Sequence[str]],
    reverse_deps: Mapping[str, Sequence[str]],
) -> list[str]:
    """Verify consistency: if A depends on B, B's reverse deps include A.

    Returns a list of error messages (empty means valid).
    """
    errors: list[str] = []
    for init_file, deps in dep_graph.items():
        for dep in deps:
            rev = reverse_deps.get(dep, [])
            if init_file not in rev:
                errors.append(
                    f"{dep} reverse deps missing {init_file}"
                )
    return errors
