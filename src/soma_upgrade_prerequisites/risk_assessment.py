#!/usr/bin/env python3
# Risk assessment functions for upgrade and security documentation.
# Scans for warning patterns, risk indicators, and new dependencies.
from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from .upgrade_set import SECURITY_SUFFIX, UPGRADE_SUFFIX

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .models import DependencyGraph



def classify_grep_matches(
    grep_results: Mapping[str, Sequence[str]],
    patterns: Sequence[str],
    suffix: str,
) -> dict[str, list[str]]:
    """Classify grep results by which specific patterns matched.

    Extracts basename from file path, strips suffix to derive init
    file name, then checks each line against each pattern.
    Returns dict mapping init file names to matched patterns.
    """
    result: dict[str, list[str]] = {}
    for path, lines in grep_results.items():
        name = PurePosixPath(path).name.removesuffix(suffix)
        matched = _match_patterns(lines, patterns)
        if matched:
            result[name] = matched
    return result


def _match_patterns(
    lines: Sequence[str], patterns: Sequence[str],
) -> list[str]:
    """Return patterns that match at least one line."""
    return [
        p for p in patterns
        if any(re.search(p, line, re.IGNORECASE) for line in lines)
    ]


def find_warned_files(
    grep_results: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    """Identify files with upgrade warning patterns."""
    from .constants import WARNING_PATTERNS

    return classify_grep_matches(
        grep_results, WARNING_PATTERNS, UPGRADE_SUFFIX,
    )


def find_high_risk_files(
    grep_results: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    """Identify files with high-risk security patterns."""
    from .constants import RISK_PATTERNS

    return classify_grep_matches(
        grep_results, RISK_PATTERNS, SECURITY_SUFFIX,
    )


def find_multi_package_files(
    graph_data: DependencyGraph,
) -> dict[str, int]:
    """Identify init files declaring more than one package.

    Returns dict mapping init file name to package count.
    """
    return {
        name: len(entry.packages)
        for name, entry in graph_data.items()
        if len(entry.packages) > 1
    }
