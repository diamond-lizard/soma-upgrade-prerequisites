#!/usr/bin/env python3
"""Pipeline step: topological sort and internal validation."""
# Pipeline step: topological sort and internal validation.
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from .constants import ReportSection
from .critical_path import compute_critical_path
from .defaults import ELPACA_INIT_FILE
from .report_sections_pipeline import make_sort_section, make_validation_section
from .topological_sort import assign_dependency_levels, compute_topological_sort
from .validation import (
    validate_reverse_deps,
    validate_topological_order,
)

if TYPE_CHECKING:
    from .pipeline_analyze import AnalysisResult
    from .pipeline_risks import RiskResult


class SortResult(NamedTuple):
    """Result of topological sort computation."""

    sorted_files: list[str]
    levels: dict[str, int]
    critical_path: list[str]


def compute_sort_and_validate(
    analysis: AnalysisResult,
    risk_result: RiskResult,
    sections: list[ReportSection],
) -> SortResult | None:
    """Compute topological sort and run validation checks.

    Returns None if cycles exist (sort is skipped).
    Raises PipelineStopError if validation checks fail.
    """
    if risk_result.cycles:
        sections.append(ReportSection(
            "Upgrade Order", "INFO", "Skipped due to dependency cycles",
        ))
        sections.append(ReportSection(
            "Validation", "INFO", "Skipped due to dependency cycles",
        ))
        return None
    return _sort_and_check(analysis, risk_result, sections)


def _sort_and_check(
    analysis: AnalysisResult,
    risk_result: RiskResult,
    sections: list[ReportSection],
) -> SortResult:
    """Run sort and validation when no cycles exist."""
    from .pipeline import PipelineStopError

    warned_keys = list(risk_result.warned.keys())
    sorted_files = compute_topological_sort(
        analysis.init_dep_graph, analysis.upgrade_set,
        warned_keys, analysis.reverse_deps, ELPACA_INIT_FILE,
    )
    levels = assign_dependency_levels(
        analysis.init_dep_graph, analysis.upgrade_set,
    )
    crit_path = compute_critical_path(
        analysis.init_dep_graph, analysis.upgrade_set,
    )
    sections.append(make_sort_section(sorted_files, crit_path))
    errors = _run_checks(analysis, sorted_files)
    sections.append(make_validation_section(errors))
    if errors:
        raise PipelineStopError
    return SortResult(sorted_files, levels, crit_path)


def _run_checks(
    analysis: AnalysisResult, sorted_files: list[str],
) -> list[str]:
    """Run graph-internal validation checks."""
    errors: list[str] = []
    errors.extend(validate_topological_order(
        sorted_files, analysis.init_dep_graph,
    ))
    errors.extend(validate_reverse_deps(
        analysis.init_dep_graph, analysis.reverse_deps,
    ))
    return errors
