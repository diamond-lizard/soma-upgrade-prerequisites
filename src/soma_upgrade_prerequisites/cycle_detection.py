#!/usr/bin/env python3
"""Cycle detection for init-file dependency graphs."""
# Cycle detection for init-file dependency graphs.
# Uses DFS to find circular dependencies.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def detect_cycles(
    dep_graph: Mapping[str, Sequence[str]],
) -> list[list[str]]:
    """Find all cycles in the dependency graph via DFS.

    Returns a list of cycles, each a list of init file names.
    Returns an empty list if no cycles exist.
    """
    visited: set[str] = set()
    in_stack: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []

    for node in dep_graph:
        if node not in visited:
            _dfs(node, dep_graph, visited, in_stack, stack, cycles)

    return cycles


def _dfs(
    node: str,
    graph: Mapping[str, Sequence[str]],
    visited: set[str],
    in_stack: set[str],
    stack: list[str],
    cycles: list[list[str]],
) -> None:
    """DFS helper for cycle detection."""
    visited.add(node)
    in_stack.add(node)
    stack.append(node)

    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            _dfs(neighbor, graph, visited, in_stack, stack, cycles)
        elif neighbor in in_stack:
            idx = stack.index(neighbor)
            cycles.append(stack[idx:])

    stack.pop()
    in_stack.discard(node)
