#!/usr/bin/env python3
# Pipeline-flow report sections: cycles, sort, validation, missing reviews.
from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import ReportSection

if TYPE_CHECKING:
    from collections.abc import Sequence


def make_cycle_section(cycles: Sequence[Sequence[str]]) -> ReportSection:
    """FAIL if cycles found, PASS if none."""
    if not cycles:
        return ReportSection("Dependency Cycles", "PASS", "")
    detail = "\n".join(" -> ".join(c) for c in cycles)
    return ReportSection("Dependency Cycles", "FAIL", detail)


def make_sort_section(
    sorted_files: Sequence[str], critical_path: Sequence[str],
) -> ReportSection:
    """INFO showing upgrade order and critical path."""
    detail = f"Order: {', '.join(sorted_files)}"
    detail += f"\nCritical path: {' -> '.join(critical_path)}"
    return ReportSection("Upgrade Order", "INFO", detail)


def make_validation_section(errors: Sequence[str]) -> ReportSection:
    """PASS if no errors, FAIL if any."""
    if not errors:
        return ReportSection("Validation", "PASS", "")
    return ReportSection("Validation", "FAIL", "\n".join(errors))


def make_missing_reviews_section(
    missing: Sequence[str],
) -> ReportSection:
    """FAIL listing init files missing security reviews."""
    detail = "\n".join(missing)
    return ReportSection("Missing Security Reviews", "FAIL", detail)
