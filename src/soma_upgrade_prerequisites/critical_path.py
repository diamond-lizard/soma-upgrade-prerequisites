#!/usr/bin/env python3
# Critical path computation for the upgrade dependency graph.
# Finds the longest dependency chain among upgrade-set members.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def compute_critical_path(
    dep_graph: Mapping[str, Sequence[str]],
    upgrade_set: Sequence[str],
) -> list[str]:
    """Compute the longest dependency chain among upgrade-set members.

    Returns the chain as a list from root (dependency) to leaf (dependent).
    Tiebreaks lexicographically for determinism.
    """
    members = set(upgrade_set)
    best: list[str] = []
    cache: dict[str, list[str]] = {}
    for node in sorted(members):
        chain = _longest_from(node, dep_graph, members, cache)
        if len(chain) > len(best):
            best = chain
    return best


def _longest_from(
    node: str,
    dep_graph: Mapping[str, Sequence[str]],
    members: set[str],
    cache: dict[str, list[str]],
) -> list[str]:
    """Find the longest chain starting from node's dependencies."""
    if node in cache:
        return cache[node]
    best_sub: list[str] = []
    for dep in sorted(dep_graph.get(node, [])):
        if dep in members:
            sub = _longest_from(dep, dep_graph, members, cache)
            if len(sub) > len(best_sub):
                best_sub = sub
    result = [*best_sub, node]
    cache[node] = result
    return result
