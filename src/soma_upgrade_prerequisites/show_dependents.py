#!/usr/bin/env python3
"""Dependents display logic for the show-tracker subcommand."""
# Dependents display logic for the show-tracker subcommand.
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from .constants import CascadeCandidate
    from .models import ProgressTracker
    from .protocols import FileSystem


def show_dependents(
    fs: FileSystem, trk: ProgressTracker, init_file: str,
    dd_path: str, graph_path: str,
) -> None:
    """Show cascade candidates and other dependents for an init file."""
    from .cascade import (
        compute_all_transitive_dependents,
        compute_cascade_candidates,
    )
    from .derived_data import read_derived_data
    from .validation_git import check_stale_derived_data

    dd = read_derived_data(fs, dd_path)
    if dd is None:
        click.echo(
            "Derived data not found. Run `write-analysis`.", err=True,
        )
        sys.exit(1)
    try:
        check_stale_derived_data(fs.read_file(graph_path), dd)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    if not any(e.init_file == init_file for e in trk.entries):
        click.echo(f"Init file '{init_file}' not found.", err=True)
        sys.exit(1)
    cascade = compute_cascade_candidates(init_file, dd.reverse_deps, trk)
    all_deps = compute_all_transitive_dependents(
        init_file, dd.reverse_deps, trk,
    )
    _print_sections(cascade, all_deps, trk)


def _print_sections(
    cascade: list[CascadeCandidate],
    all_deps: list[CascadeCandidate],
    trk: ProgressTracker,
) -> None:
    """Format and print cascade and other dependents sections."""
    cascade_files = {c.init_file for c in cascade}
    others = [d for d in all_deps if d.init_file not in cascade_files]
    status_map = {e.init_file: e.status for e in trk.entries}
    if not cascade and not others:
        click.echo("No dependents in tracker.")
        return
    if cascade:
        click.echo("Cascade candidates:")
        for c in cascade:
            click.echo(f"  {c.position}. {c.init_file}")
    if others:
        click.echo("Other dependents (not eligible for cascade):")
        for d in others:
            click.echo(f"  - {d.init_file} ({status_map[d.init_file]})")
