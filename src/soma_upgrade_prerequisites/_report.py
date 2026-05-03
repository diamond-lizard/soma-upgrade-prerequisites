#!/usr/bin/env python3
"""Validation result reporting."""
from __future__ import annotations

import sys

import click


def report_and_exit(errors: dict[str, list[str]]) -> None:
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
