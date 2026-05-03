#!/usr/bin/env python3
"""Low-level git subprocess helpers for boundary-aware log queries."""
from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from .protocols import GitBoundaryError

if TYPE_CHECKING:
    from pathlib import Path


def rev_parse_commit(ref: str, cwd: Path) -> str | None:
    """Try to resolve ref to a commit SHA; return None on failure."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        capture_output=True, text=True, cwd=cwd,
    )
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None


def verify_ancestry(
    start_ref: str, start_sha: str,
    branch_ref: str, branch_tip: str,
    cwd: Path,
) -> None:
    """Verify start_sha is an ancestor of branch_tip.

    Exit code 0: confirmed. Exit code 1: not ancestor (GitBoundaryError).
    Exit code >1: git operational error (ValueError).
    """
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", start_sha, branch_tip],
        capture_output=True, text=True, cwd=cwd,
    )
    if result.returncode == 1:
        msg = f"starting_commit '{start_ref}' is not an ancestor of branch '{branch_ref}'"
        raise GitBoundaryError(msg)
    if result.returncode > 1:
        detail = result.stderr.strip()
        msg = f"git merge-base failed{': ' + detail if detail else ''}"
        raise ValueError(msg)


def log_range(start_sha: str, end_sha: str, cwd: Path) -> list[str]:
    """Return log lines for the exclusive range between two resolved SHAs."""
    result = subprocess.run(
        ["git", "log", "--oneline", f"{start_sha}..{end_sha}"],
        capture_output=True, text=True, cwd=cwd,
    )
    if result.returncode != 0:
        detail = result.stderr.strip()
        msg = f"git log failed{': ' + detail if detail else ''}"
        raise ValueError(msg)
    return [line.strip() for line in result.stdout.splitlines()]
