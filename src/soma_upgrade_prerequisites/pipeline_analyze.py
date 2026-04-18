#!/usr/bin/env python3
"""Pipeline step: dependency analysis, orphan detection, upgrade set."""
# Pipeline step: dependency analysis, orphan detection, upgrade set.
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from .constants import ReportSection
from .graph import (
    build_init_file_dep_graph,
    build_package_to_init_mapping,
    build_reverse_deps,
    validate_depended_on_by,
)
from .orphan_detection import find_orphan_packages
from .report_sections import make_depended_on_by_section, make_orphan_section
from .upgrade_set import list_upgrade_files

if TYPE_CHECKING:
    from .config import PipelineConfig
    from .pipeline_load import GraphResult
    from .protocols import FileSystem


class AnalysisResult(NamedTuple):
    """Result of dependency analysis."""

    pkg_to_init: dict[str, str]
    init_to_packages: dict[str, list[str]]
    init_dep_graph: dict[str, list[str]]
    reverse_deps: dict[str, list[str]]
    upgrade_set: list[str]


def analyze_dependencies(
    fs: FileSystem,
    config: PipelineConfig,
    graph_result: GraphResult,
    sections: list[ReportSection],
) -> AnalysisResult:
    """Run dependency analysis and return results.

    Appends orphan and depended_on_by sections.
    Raises PipelineStopError if upgrade set has uncovered init files.
    """
    from .pipeline import PipelineStopError

    graph = graph_result.graph_data
    pkg_to_init = build_package_to_init_mapping(graph)
    init_to_packages = _build_init_to_packages(pkg_to_init)
    dep_graph = build_init_file_dep_graph(graph, pkg_to_init)
    reverse = build_reverse_deps(dep_graph)
    orphans = find_orphan_packages(
        graph, pkg_to_init, fs, config.inits_dir, config.upgrades_dir,
    )
    dep_errors = validate_depended_on_by(graph, reverse)
    sections.append(make_orphan_section(orphans))
    sections.append(make_depended_on_by_section(dep_errors))
    upgrade_set = list_upgrade_files(fs, config.upgrades_dir)
    uncovered = [f for f in upgrade_set if f not in graph]
    if uncovered:
        sections.append(ReportSection(
            "Upgrade Set Coverage", "FAIL",
            "Init files not in graph: " + ", ".join(uncovered),
        ))
        raise PipelineStopError
    return AnalysisResult(
        pkg_to_init, init_to_packages, dep_graph, reverse, upgrade_set,
    )


def _build_init_to_packages(
    pkg_to_init: dict[str, str],
) -> dict[str, list[str]]:
    """Build inverse mapping: init file -> list of packages."""
    result: dict[str, list[str]] = {}
    for pkg, init in pkg_to_init.items():
        result.setdefault(init, []).append(pkg)
    return result
