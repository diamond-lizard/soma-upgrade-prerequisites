#!/usr/bin/env python3
"""Shared options and runner for preview-analysis / write-analysis."""
# Shared options and runner for preview-analysis / write-analysis.
from __future__ import annotations

import functools
import sys
from typing import TYPE_CHECKING

import click

from .defaults import (
    DEFAULT_BRANCH,
    DEFAULT_DERIVED_DATA_PATH,
    DEFAULT_GRAPH_JSON,
    DEFAULT_INITS_DIR,
    DEFAULT_TRACKER_PATH,
    DEFAULT_UPGRADES_DIR,
)

if TYPE_CHECKING:
    from .models import ProgressTracker
    from .protocols import FileSystem


def analysis_options(fn: click.decorators.FC) -> click.decorators.FC:
    """Apply the six shared path/branch options to an analysis command."""
    options = [
        click.option(
            "--derived-data-path",
            default=DEFAULT_DERIVED_DATA_PATH,
            show_default=True,
        ),
        click.option(
            "--tracker-path",
            default=DEFAULT_TRACKER_PATH,
            show_default=True,
        ),
        click.option("--branch", default=DEFAULT_BRANCH, show_default=True),
        click.option(
            "--inits-dir", default=DEFAULT_INITS_DIR, show_default=True,
        ),
        click.option(
            "--upgrades-dir",
            default=DEFAULT_UPGRADES_DIR,
            show_default=True,
        ),
        click.option(
            "--graph-json",
            default=DEFAULT_GRAPH_JSON,
            show_default=True,
        ),
    ]
    return functools.reduce(lambda f, opt: opt(f), options, fn)


def run_analysis(
    *,
    write: bool,
    graph_json: str,
    upgrades_dir: str,
    inits_dir: str,
    branch: str,
    tracker_path: str,
    derived_data_path: str,
) -> None:
    """Run the analysis pipeline (shared by preview-analysis and write-analysis)."""
    from .config import PipelineConfig
    from .defaults import DEFAULT_REPO_PATH
    from .filesystem import RealFileSystem
    from .git_client import RealGitClient
    from .pipeline import run_generate_pipeline

    fs = RealFileSystem()
    git = RealGitClient(DEFAULT_REPO_PATH)
    existing = _load_existing_tracker(fs, tracker_path) if write else None
    config = PipelineConfig(
        graph_json_path=graph_json,
        upgrades_dir=upgrades_dir,
        inits_dir=inits_dir,
        branch=branch,
        tracker_path=tracker_path,
        derived_data_path=derived_data_path,
    )
    report, code = run_generate_pipeline(
        fs, git, config, write, existing,
    )
    click.echo(report)
    sys.exit(code)


def _load_existing_tracker(
    fs: FileSystem, tracker_path: str,
) -> ProgressTracker | None:
    """Load existing tracker for write-analysis (returns None if absent)."""
    from pydantic import ValidationError

    from .tracker_io import read_tracker

    try:
        return read_tracker(fs, tracker_path)
    except (ValidationError, ValueError) as exc:
        click.echo(f"Error reading tracker: {exc}", err=True)
        sys.exit(1)
