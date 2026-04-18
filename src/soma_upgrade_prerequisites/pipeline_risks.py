#!/usr/bin/env python3
# Pipeline step: risk assessment (cycles, warnings, security, new deps).
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from .cycle_detection import detect_cycles
from .new_deps import find_new_deps_files
from .pipeline_grep import grep_and_classify_risks, grep_and_classify_warnings
from .report_sections import (
    make_high_risk_section,
    make_multi_pkg_section,
    make_new_deps_section,
    make_warning_section,
)
from .report_sections_pipeline import (
    make_cycle_section,
    make_missing_reviews_section,
)
from .risk_assessment import (
    find_missing_security_reviews,
    find_multi_package_files,
)

if TYPE_CHECKING:
    from .config import PipelineConfig
    from .constants import ReportSection
    from .pipeline_analyze import AnalysisResult
    from .pipeline_load import GraphResult
    from .protocols import FileSystem


class RiskResult(NamedTuple):
    """Result of risk assessment."""

    warned: dict[str, list[str]]
    high_risk: dict[str, list[str]]
    multi_pkg: dict[str, int]
    new_deps: list[str]
    cycles: list[list[str]]


def assess_risks(
    fs: FileSystem,
    config: PipelineConfig,
    graph_result: GraphResult,
    analysis: AnalysisResult,
    sections: list[ReportSection],
) -> RiskResult:
    """Assess risks and append report sections.

    Raises PipelineStopError if security reviews are missing.
    """
    from .pipeline import PipelineStopError

    cycles = detect_cycles(analysis.init_dep_graph)
    sections.append(make_cycle_section(cycles))
    warned = grep_and_classify_warnings(fs, config, analysis)
    sections.append(make_warning_section(warned))
    missing = find_missing_security_reviews(
        analysis.upgrade_set, fs, config.upgrades_dir,
    )
    if missing:
        sections.append(make_missing_reviews_section(missing))
        raise PipelineStopError
    high_risk = grep_and_classify_risks(fs, config, analysis)
    sections.append(make_high_risk_section(high_risk))
    multi_pkg = find_multi_package_files(graph_result.graph_data)
    new_deps = find_new_deps_files(
        fs, config.upgrades_dir, analysis.upgrade_set,
    )
    sections.append(make_multi_pkg_section(multi_pkg))
    sections.append(make_new_deps_section(new_deps))
    return RiskResult(warned, high_risk, multi_pkg, new_deps, cycles)

