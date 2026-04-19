#!/usr/bin/env python3
"""CLI subcommand: preview-analysis (dry-run analysis report)."""
# CLI subcommand: preview-analysis (dry-run analysis report).
from __future__ import annotations

import click

from .cmd_analysis import analysis_options, run_analysis


@click.command("preview-analysis")
@analysis_options
def preview_analysis(
    graph_json: str,
    upgrades_dir: str,
    inits_dir: str,
    branch: str,
    tracker_path: str,
    derived_data_path: str,
) -> None:
    """Run the analysis pipeline and print a report (no files written)."""
    run_analysis(
        write=False,
        graph_json=graph_json,
        upgrades_dir=upgrades_dir,
        inits_dir=inits_dir,
        branch=branch,
        tracker_path=tracker_path,
        derived_data_path=derived_data_path,
    )
