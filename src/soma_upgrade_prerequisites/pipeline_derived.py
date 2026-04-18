#!/usr/bin/env python3
# Derived dependency data construction for pipeline output.
from __future__ import annotations

import hashlib

from .defaults import DERIVED_DATA_SCHEMA_VERSION
from .models import DerivedDependencyData


def create_derived_data(
    pkg_to_init: dict[str, str],
    init_to_packages: dict[str, list[str]],
    init_dep_graph: dict[str, list[str]],
    reverse_deps: dict[str, list[str]],
    sorted_files: list[str],
    graph_json_content: str,
) -> DerivedDependencyData:
    """Construct a DerivedDependencyData with computed SHA-256 hash."""
    graph_hash = hashlib.sha256(graph_json_content.encode()).hexdigest()
    return DerivedDependencyData(
        schema_version=DERIVED_DATA_SCHEMA_VERSION,
        source_graph_hash=graph_hash,
        pkg_to_init=pkg_to_init,
        init_to_packages=init_to_packages,
        init_dep_graph=init_dep_graph,
        reverse_deps=reverse_deps,
        sorted_files=sorted_files,
    )
