#!/usr/bin/env python3
# Dependency graph construction functions.
# Builds mappings, init-file dependency graphs, and reverse dependencies.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
