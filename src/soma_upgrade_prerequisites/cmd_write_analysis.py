#!/usr/bin/env python3
"""CLI subcommand: write-analysis (run pipeline and write output files)."""
# CLI subcommand: write-analysis (run pipeline and write output files).
from __future__ import annotations

import click

from .cmd_analysis import analysis_options, run_analysis


@click.command("write-analysis")
@analysis_options
def write_analysis(
    graph_json: str,
    upgrades_dir: str,
    inits_dir: str,
    branch: str,
    tracker_path: str,
    derived_data_path: str,
) -> None:
    """Run the analysis pipeline and write tracker and derived data files."""
    run_analysis(
        write=True,
        graph_json=graph_json,
        upgrades_dir=upgrades_dir,
        inits_dir=inits_dir,
        branch=branch,
        tracker_path=tracker_path,
        derived_data_path=derived_data_path,
    )
