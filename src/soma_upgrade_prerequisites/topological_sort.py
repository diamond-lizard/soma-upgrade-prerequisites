#!/usr/bin/env python3
# Topological sort, dependency levels, and critical path computation.
# Orders init files for the upgrade campaign.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def compute_topological_sort(
    dep_graph: Mapping[str, Sequence[str]],
    upgrade_set: Sequence[str],
    warned_files: Sequence[str],
    reverse_deps: Mapping[str, Sequence[str]],
    elpaca_init: str,
) -> list[str]:
    """Sort upgrade_set by: elpaca first, deps before dependents,
    warned early, more dependents first.
    """
    levels = assign_dependency_levels(dep_graph, upgrade_set)
    warned = set(warned_files)
    return sorted(
        upgrade_set,
        key=lambda f: (
            f != elpaca_init,
            levels.get(f, 0),
            f not in warned,
            -len(reverse_deps.get(f, [])),
            f,
        ),
    )


def _transitive_upgrade_deps(
    node: str,
    dep_graph: Mapping[str, Sequence[str]],
    upgrade_members: set[str],
) -> set[str]:
    """Find all upgrade-set members reachable from node."""
    visited: set[str] = set()
    stack = list(dep_graph.get(node, []))
    result: set[str] = set()
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        if current in upgrade_members and current != node:
            result.add(current)
        stack.extend(dep_graph.get(current, []))
    return result


def assign_dependency_levels(
    dep_graph: Mapping[str, Sequence[str]],
    upgrade_set: Sequence[str],
) -> dict[str, int]:
    """Assign dependency levels to upgrade-set members.

    Level 0 = no transitive deps on other upgrade-set members.
    Level N = max(level of transitive upgrade-set deps) + 1.
    Non-upgrade-set nodes serve as intermediaries but get no level.
    """
    members = set(upgrade_set)
    trans: dict[str, set[str]] = {
        m: _transitive_upgrade_deps(m, dep_graph, members)
        for m in members
    }
    levels: dict[str, int] = {}
    remaining = set(members)
    level = 0
    while remaining:
        batch = {
            m for m in remaining
            if all(d in levels for d in trans[m])
        }
        if not batch:
            for m in remaining:
                levels[m] = level
            break
        for m in batch:
            levels[m] = level
        remaining -= batch
        level += 1
    return levels
