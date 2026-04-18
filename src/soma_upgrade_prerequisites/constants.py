#!/usr/bin/env python3
# Domain types, status constants, and pattern definitions.
from __future__ import annotations

from typing import Literal, NamedTuple

# Status of a tracker entry in the upgrade workflow.
Status = Literal[
    "pending", "in-progress", "upgraded", "skipped", "blocked", "reverted",
]

# Flag indicating a special condition on a tracker entry.
Flag = Literal["warned", "high-risk", "new-deps", "multi-pkg"]

# Severity level for report sections.
ReportLevel = Literal["PASS", "WARN", "FAIL", "INFO"]

# Statuses that represent a completed decision (no further action).
TERMINAL_STATUSES: tuple[Status, ...] = (
    "upgraded", "skipped", "blocked", "reverted",
)

# Statuses preserved from existing tracker during regeneration.
PRESERVED_STATUSES: tuple[Status, ...] = (
    *TERMINAL_STATUSES, "in-progress",
)

# Statuses that trigger forward cascade (block dependents).
FORWARD_CASCADE_STATUSES: tuple[Status, ...] = ("skipped", "reverted")

# Statuses that trigger reverse cascade when changed away from.
# Includes "blocked" for cascade stacking scenarios.
REVERSE_CASCADE_STATUSES: tuple[Status, ...] = (
    "skipped", "blocked", "reverted",
)


class ReportSection(NamedTuple):
    """A single section in the generate report output."""

    title: str
    level: ReportLevel
    detail: str


class CascadeCandidate(NamedTuple):
    """A dependent entry eligible for cascade blocking."""

    position: int
    init_file: str

# Regex patterns for detecting upgrade warnings in upgrade-process.md files.
# Context-specific patterns avoid false positives from technical descriptions
# (e.g., bare "skip" matches function names like yas-skip-and-clear-field).
WARNING_PATTERNS: list[str] = [
    r"do not upgrade",
    r"not recommended",
    r"advise against",
    r"\bdefer this\b.*upgrade",
    r"recommend(?:ation)?:?\s*skip",
]

# Patterns for detecting high-risk indicators in security-review.md files.
RISK_PATTERNS: list[str] = [
    "high risk",
    "high-risk",
    "critical",
    "vulnerability",
    "CVE",
    "remote code execution",
    "arbitrary code",
    "supply chain",
]

# Header marking the "New Dependencies" section in upgrade-process.md files.
NEW_DEPS_HEADER: str = "## 3. New Dependencies"

# Patterns indicating no new dependencies (matched case-insensitively).
NEW_DEPS_NONE_PATTERNS: list[str] = ["none", "no new", "no non-built-in"]

# Classification of orphan packages found in dependency graph.
# misidentified: matching init file exists under a different package name.
# dependency-not-to-be-upgraded: init file exists on disk but not in graph.
# missing-from-multi-package: init file in graph but omits this package.
# unresolvable: no matching init file exists on disk.
OrphanClassification = Literal[
    "misidentified",
    "dependency-not-to-be-upgraded",
    "missing-from-multi-package",
    "unresolvable",
]
