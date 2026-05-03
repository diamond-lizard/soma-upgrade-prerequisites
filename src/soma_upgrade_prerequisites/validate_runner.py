#!/usr/bin/env python3
"""Validation orchestration: load data, run checks, report results."""
# Validation orchestration: load data, run checks, report results.
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import click

from .derived_data import read_derived_data
from .models import DependencyGraph
from .protocols import GitBoundaryError
from .validation import (
    validate_mapping_completeness,
    validate_reverse_deps,
    validate_topological_order,
    validate_tracker_vs_sort,
)
from .validation_git import check_stale_derived_data, validate_tracker_vs_git

if TYPE_CHECKING:
    from .config import ValidateConfig
    from .models import DerivedDependencyData, ProgressTracker
    from .protocols import FileSystem, GitClient


def run_validation(
    fs: FileSystem, git: GitClient,
    config: ValidateConfig, trk: ProgressTracker,
) -> None:
    """Load data, run all five checks, print results, exit code."""
    dd = _load_derived(fs, config)
    graph_content = fs.read_file(config.graph_json_path)
    check_stale_derived_data(graph_content, dd)
    graph_data = DependencyGraph.model_validate_json(graph_content)
    git_errors = _check_tracker_vs_git(git, config.branch, trk)
    errors = _collect_errors(graph_data, dd, trk, git_errors)
    _report_and_exit(errors)


def _load_derived(
    fs: FileSystem, config: ValidateConfig,
) -> DerivedDependencyData:
    """Load derived data or raise ValueError if missing."""
    dd = read_derived_data(fs, config.derived_data_path)
    if dd is None:
        msg = "Derived data not found. Run `write-analysis` first."
        raise ValueError(msg)
    return dd


def _check_tracker_vs_git(
    git: GitClient, branch: str, trk: ProgressTracker,
) -> list[str]:
    """Run tracker-vs-git check with boundary scoping.

    Boundary errors are non-fatal (reported as check errors).
    Infrastructure errors (plain ValueError) propagate to the caller.
    """
    try:
        git_lines = git.get_log_lines_since(branch, trk.starting_commit)
    except GitBoundaryError as exc:
        return [str(exc)]
    return validate_tracker_vs_git(trk, git_lines)


def _collect_errors(
    graph_data: DependencyGraph, dd: DerivedDependencyData,
    trk: ProgressTracker, git_errors: list[str],
) -> dict[str, list[str]]:
    """Run all five checks; git errors are pre-computed by caller."""
    return {
        "Mapping completeness": validate_mapping_completeness(
            graph_data, dd.pkg_to_init,
        ),
        "Topological order": validate_topological_order(
            dd.sorted_files, dd.init_dep_graph,
        ),
        "Reverse deps": validate_reverse_deps(
            dd.init_dep_graph, dd.reverse_deps,
        ),
        "Tracker vs sort": validate_tracker_vs_sort(
            trk, dd.sorted_files,
        ),
        "Tracker vs git": git_errors,
    }


def _report_and_exit(errors: dict[str, list[str]]) -> None:
    """Print results grouped by check and exit with appropriate code."""
    has_errors = False
    for check, msgs in errors.items():
        if msgs:
            has_errors = True
            click.echo(f"\n{check}:")
            for msg in msgs:
                click.echo(f"  - {msg}")
    if has_errors:
        sys.exit(1)
    click.echo("All validation checks passed.")
