#!/usr/bin/env python3
"""Pipeline step: assemble outputs and write files."""
# Pipeline step: assemble outputs and write files.
from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import ReportSection
from .derived_data import write_derived_data
from .pipeline_derived import create_derived_data
from .pipeline_flags import assemble_flags
from .progress_tracker import create_tracker
from .tracker_io import write_tracker
from .tracker_preserve import preserve_statuses

if TYPE_CHECKING:
    from .config import PipelineConfig
    from .models import ProgressTracker
    from .pipeline_analyze import AnalysisResult
    from .pipeline_load import GraphResult
    from .pipeline_risks import RiskResult
    from .pipeline_sort import SortResult
    from .protocols import FileSystem


def finalize_outputs(
    fs: FileSystem,
    config: PipelineConfig,
    graph_result: GraphResult,
    analysis: AnalysisResult,
    risk_result: RiskResult,
    sort_result: SortResult | None,
    write: bool,
    existing_tracker: ProgressTracker | None,
    sections: list[ReportSection],
) -> None:
    """Assemble outputs, write files if requested.

    Prepends header section. Raises PipelineStopError if FAIL sections exist.
    """
    from .pipeline import PipelineStopError

    sections.insert(0, ReportSection(
        "Generate Summary", "INFO",
        f"Starting commit: {graph_result.starting_commit}\n"
        f"Upgrade set: {len(analysis.upgrade_set)} init files",
    ))
    if any(s.level == "FAIL" for s in sections):
        raise PipelineStopError
    if write and sort_result is not None:
        _write_outputs(
            fs, config, graph_result, analysis,
            risk_result, sort_result, existing_tracker, sections,
        )
    elif not write:
        sections.append(ReportSection(
            "Output", "INFO", "Dry run -- no files written",
        ))


def _write_outputs(
    fs: FileSystem,
    config: PipelineConfig,
    graph_result: GraphResult,
    analysis: AnalysisResult,
    risk_result: RiskResult,
    sort_result: SortResult,
    existing_tracker: ProgressTracker | None,
    sections: list[ReportSection],
) -> None:
    """Write tracker and derived data files."""
    flags = assemble_flags(
        risk_result.warned, risk_result.high_risk,
        risk_result.multi_pkg, risk_result.new_deps,
        analysis.upgrade_set,
    )
    tracker = create_tracker(
        graph_result.starting_commit,
        sort_result.sorted_files,
        graph_result.graph_data,
        sort_result.levels,
        flags,
    )
    if existing_tracker is not None:
        tracker = preserve_statuses(
            tracker, existing_tracker, analysis.init_dep_graph,
        )
    derived = create_derived_data(
        analysis.pkg_to_init, analysis.init_to_packages,
        analysis.init_dep_graph, analysis.reverse_deps,
        sort_result.sorted_files, graph_result.graph_content,
    )
    write_derived_data(fs, config.derived_data_path, derived)
    write_tracker(fs, config.tracker_path, tracker, backup=True)
    sections.append(ReportSection(
        "Output", "INFO", "Files written successfully",
    ))
