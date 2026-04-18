#!/usr/bin/env python3
# Per-check section helpers for the generate report.
# Each helper returns a ReportSection for one pipeline check.
from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import ReportSection

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .models import OrphanPackage



def make_orphan_section(orphans: Sequence[OrphanPackage]) -> ReportSection:
    """WARN if orphans found, PASS if none."""
    if not orphans:
        return ReportSection("Orphan Packages", "PASS", "")
    lines = [f"{o.package}: {o.classification}" for o in orphans]
    return ReportSection("Orphan Packages", "WARN", "\n".join(lines))


def make_depended_on_by_section(errors: Sequence[str]) -> ReportSection:
    """WARN if discrepancies, PASS if consistent."""
    if not errors:
        return ReportSection("depended_on_by Consistency", "PASS", "")
    return ReportSection(
        "depended_on_by Consistency", "WARN", "\n".join(errors),
    )


def make_warning_section(
    warned: Mapping[str, Sequence[str]],
) -> ReportSection:
    """WARN if warned files found, PASS if none."""
    if not warned:
        return ReportSection("Warning Flags", "PASS", "")
    lines = [f"{k}: {', '.join(v)}" for k, v in warned.items()]
    return ReportSection("Warning Flags", "WARN", "\n".join(lines))


def make_high_risk_section(
    high_risk: Mapping[str, Sequence[str]],
) -> ReportSection:
    """WARN if high-risk files found, PASS if none."""
    if not high_risk:
        return ReportSection("High-Risk Flags", "PASS", "")
    lines = [f"{k}: {', '.join(v)}" for k, v in high_risk.items()]
    return ReportSection("High-Risk Flags", "WARN", "\n".join(lines))


def make_multi_pkg_section(
    multi_pkg: Mapping[str, int],
) -> ReportSection:
    """INFO listing multi-package init files."""
    if not multi_pkg:
        return ReportSection("Multi-Package Init Files", "INFO", "None")
    lines = [f"{k}: {v} packages" for k, v in multi_pkg.items()]
    return ReportSection(
        "Multi-Package Init Files", "INFO", "\n".join(lines),
    )


def make_new_deps_section(new_deps: Sequence[str]) -> ReportSection:
    """WARN if new deps found, PASS if none."""
    if not new_deps:
        return ReportSection("New Dependencies", "PASS", "")
    return ReportSection(
        "New Dependencies", "WARN", "\n".join(new_deps),
    )

