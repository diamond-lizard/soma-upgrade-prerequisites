#!/usr/bin/env python3
"""CLI subcommand: validate (check tracker/data consistency)."""
# CLI subcommand: validate (check tracker/data consistency).
from __future__ import annotations

import sys

import click

from .defaults import (
    DEFAULT_BRANCH,
    DEFAULT_DERIVED_DATA_PATH,
    DEFAULT_GRAPH_JSON,
    DEFAULT_TRACKER_PATH,
)


@click.command()
@click.option("--tracker", default=DEFAULT_TRACKER_PATH, show_default=True)
@click.option("--branch", default=DEFAULT_BRANCH, show_default=True)
@click.option("--graph-json", default=DEFAULT_GRAPH_JSON, show_default=True)
@click.option("--derived-data", default=DEFAULT_DERIVED_DATA_PATH)
def validate(
    tracker: str, branch: str,
    graph_json: str, derived_data: str,
) -> None:
    """Check consistency of tracker, dependency data, and git history."""
    import pydantic

    from .config import ValidateConfig
    from .defaults import DEFAULT_REPO_PATH
    from .filesystem import RealFileSystem
    from .git_client import RealGitClient
    from .tracker_io import read_tracker

    fs = RealFileSystem()
    git = RealGitClient(DEFAULT_REPO_PATH)
    config = ValidateConfig(
        tracker_path=tracker, branch=branch,
        graph_json_path=graph_json, derived_data_path=derived_data,
    )
    try:
        trk = read_tracker(fs, config.tracker_path)
    except (ValueError, pydantic.ValidationError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    if trk is None:
        click.echo("Tracker not found. Run `generate --write`.", err=True)
        sys.exit(1)
    try:
        from .validate_runner import run_validation

        run_validation(fs, git, config, trk)
    except (ValueError, pydantic.ValidationError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
