#!/usr/bin/env python3
# Core report formatting: section formatting and report assembly.
from __future__ import annotations

from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .constants import ReportLevel, ReportSection

_LEVEL_COLORS: dict[str, str | None] = {
    "PASS": "green",
    "WARN": "yellow",
    "FAIL": "red",
    "INFO": None,
}


def format_section(
    title: str, level: ReportLevel, detail: str,
) -> str:
    """Format a single report section with colored level label.

    Format: '=== {title} === {level}' header, then optional
    detail lines indented with 4 spaces.
    """
    color = _LEVEL_COLORS.get(level)
    styled = click.style(level, fg=color) if color else level
    header = f"=== {title} === {styled}"
    if not detail:
        return header
    indented = "\n".join(f"    {line}" for line in detail.splitlines())
    return f"{header}\n{indented}"


def build_generate_report(
    sections: Sequence[ReportSection],
) -> tuple[str, int]:
    """Join report sections and compute exit code.

    Returns (report_string, exit_code). Exit code is 1 if any
    section has level FAIL, otherwise 0.
    """
    parts = [format_section(s.title, s.level, s.detail) for s in sections]
    report = "\n\n".join(parts)
    has_fail = any(s.level == "FAIL" for s in sections)
    return report, 1 if has_fail else 0
