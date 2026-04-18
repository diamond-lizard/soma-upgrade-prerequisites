#!/usr/bin/env python3
"""Thin pipeline orchestrator for the generate subcommand."""
# Thin pipeline orchestrator for the generate subcommand.
# Calls step functions in sequence; zero decision logic.
from __future__ import annotations

from typing import TYPE_CHECKING

from .pipeline_analyze import analyze_dependencies
from .pipeline_finalize import finalize_outputs
from .pipeline_load import load_and_parse_graph
from .pipeline_risks import assess_risks
from .pipeline_sort import compute_sort_and_validate
from .report import build_generate_report

if TYPE_CHECKING:
    from .config import PipelineConfig
    from .constants import ReportSection
    from .models import ProgressTracker
    from .protocols import FileSystem, GitClient


class PipelineStopError(Exception):
    """Raised by step functions to abort the pipeline on fatal errors."""


def run_generate_pipeline(
    fs: FileSystem,
    git: GitClient,
    config: PipelineConfig,
    write: bool,
    existing_tracker: ProgressTracker | None,
) -> tuple[str, int]:
    """Run the full generate pipeline and return (report, exit_code)."""
    sections: list[ReportSection] = []
    try:
        graph_result = load_and_parse_graph(fs, git, config, sections)
        analysis = analyze_dependencies(fs, config, graph_result, sections)
        risk_result = assess_risks(fs, config, graph_result, analysis, sections)
        sort_result = compute_sort_and_validate(analysis, risk_result, sections)
        finalize_outputs(
            fs, config, graph_result, analysis, risk_result,
            sort_result, write, existing_tracker, sections,
        )
    except PipelineStopError:
        pass
    return build_generate_report(sections)
