#!/usr/bin/env python3
# Validation checks for dependency data consistency.
# Pure functions that return lists of error messages.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

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
