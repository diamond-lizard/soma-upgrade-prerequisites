#!/usr/bin/env python3
# Grep helpers for pipeline risk assessment.
from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import RISK_PATTERNS, WARNING_PATTERNS
from .risk_assessment import find_high_risk_files, find_warned_files
from .upgrade_set import build_security_path, build_upgrade_path

if TYPE_CHECKING:
    from .config import PipelineConfig
    from .pipeline_analyze import AnalysisResult
    from .protocols import FileSystem


def grep_and_classify_warnings(
    fs: FileSystem, config: PipelineConfig, analysis: AnalysisResult,
) -> dict[str, list[str]]:
    """Grep upgrade-process.md files for warning patterns."""
    paths = [
        build_upgrade_path(config.upgrades_dir, f)
        for f in analysis.upgrade_set
    ]
    combined = "|".join(WARNING_PATTERNS)
    grep_results = fs.grep_files(combined, paths)
    return find_warned_files(grep_results)


def grep_and_classify_risks(
    fs: FileSystem, config: PipelineConfig, analysis: AnalysisResult,
) -> dict[str, list[str]]:
    """Grep security-review.md files for risk patterns."""
    paths = [
        build_security_path(config.upgrades_dir, f)
        for f in analysis.upgrade_set
    ]
    combined = "|".join(RISK_PATTERNS)
    grep_results = fs.grep_files(combined, paths)
    return find_high_risk_files(grep_results)
