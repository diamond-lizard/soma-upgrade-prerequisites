#!/usr/bin/env python3
"""Git-related validation: tracker-vs-git and stale derived data checks."""
# Git-related validation: tracker-vs-git and stale derived data checks.
from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .constants import Status
    from .models import DerivedDependencyData, ProgressTracker

_UPGRADE_RE = re.compile(r"\[([^\]]+)\] Upgrade .+ from ")


def validate_tracker_vs_git(
    tracker: ProgressTracker,
    git_log_lines: Sequence[str],
) -> list[str]:
    """Verify tracker entries are consistent with git history.

    Checks: (a) every upgraded entry has a matching commit,
    (b) every upgrade commit has a matching upgraded or reverted entry.
    """
    commit_inits = _extract_upgrade_inits(git_log_lines)
    entry_map = {e.init_file: e.status for e in tracker.entries}
    errors: list[str] = []
    _check_upgraded_have_commits(entry_map, commit_inits, errors)
    _check_commits_have_entries(entry_map, commit_inits, errors)
    return errors


def _extract_upgrade_inits(
    log_lines: Sequence[str],
) -> set[str]:
    """Extract init file names from upgrade commit lines."""
    result: set[str] = set()
    for line in log_lines:
        m = _UPGRADE_RE.search(line)
        if m:
            result.add(m.group(1))
    return result


def _check_upgraded_have_commits(
    entry_map: Mapping[str, Status],
    commit_inits: set[str],
    errors: list[str],
) -> None:
    """Check every upgraded entry has a matching commit."""
    for init_file, status in entry_map.items():
        if status == "upgraded" and init_file not in commit_inits:
            errors.append(
                f"'{init_file}' is upgraded but has no matching commit"
            )


def _check_commits_have_entries(
    entry_map: Mapping[str, Status],
    commit_inits: set[str],
    errors: list[str],
) -> None:
    """Check every upgrade commit has a matching entry."""
    valid = {"upgraded", "reverted"}
    for init_file in commit_inits:
        if entry_map.get(init_file) not in valid:
            errors.append(
                f"Upgrade commit for '{init_file}' has no matching "
                "upgraded or reverted entry"
            )


def check_stale_derived_data(
    graph_json_content: str,
    derived_data: DerivedDependencyData,
) -> None:
    """Raise ValueError if graph JSON has changed since generation.

    Compares SHA-256 of content against stored hash.
    """
    current = hashlib.sha256(graph_json_content.encode()).hexdigest()
    if current != derived_data.source_graph_hash:
        msg = (
            "Dependency graph has changed since derived data was "
            "generated. Please re-run `generate --write`."
        )
        raise ValueError(msg)
