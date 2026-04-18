#!/usr/bin/env python3
# Shared helpers for progress tracker tests.
from __future__ import annotations

from soma_upgrade_prerequisites.models import (
    ProgressTracker,
    TrackerEntry,
)


def make_tracker(entries: list[TrackerEntry]) -> ProgressTracker:
    """Build a minimal ProgressTracker with given entries."""
    return ProgressTracker(
        schema_version=1,
        starting_commit="abc",
        generated_at="2026-01-01",
        status_definitions={},
        entries=entries,
    )


def make_entry(
    init_file: str = "a.el",
    status: str = "pending",
    notes: str = "",
    blocked_by: list[str] | None = None,
) -> TrackerEntry:
    """Build a minimal TrackerEntry."""
    return TrackerEntry(
        order=1, init_file=init_file, package="pkg",
        level=0, flags=[], status=status, notes=notes,
        blocked_by=blocked_by or [],
    )
