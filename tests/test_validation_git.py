#!/usr/bin/env python3
# Tests for validate_tracker_vs_git and check_stale_derived_data.
from __future__ import annotations

import hashlib

import pytest

from soma_upgrade_prerequisites.models import DerivedDependencyData
from soma_upgrade_prerequisites.validation_git import (
    check_stale_derived_data,
    validate_tracker_vs_git,
)
from tests.tracker_test_helpers import make_entry, make_tracker


def test_upgraded_with_matching_commit() -> None:
    """No error when upgraded entry has a matching commit."""
    tracker = make_tracker([make_entry("a.el", "upgraded")])
    log = ["abc1234 [a.el] Upgrade pkg from v1 to v2"]
    assert validate_tracker_vs_git(tracker, log) == []


def test_upgraded_without_matching_commit() -> None:
    """Error when upgraded entry has no matching commit."""
    tracker = make_tracker([make_entry("a.el", "upgraded")])
    errors = validate_tracker_vs_git(tracker, [])
    assert len(errors) == 1
    assert "a.el" in errors[0]


def test_commit_without_matching_entry() -> None:
    """Error when upgrade commit has no matching upgraded/reverted entry."""
    tracker = make_tracker([make_entry("a.el", "pending")])
    log = ["abc [a.el] Upgrade pkg from v1 to v2"]
    errors = validate_tracker_vs_git(tracker, log)
    assert len(errors) == 1


def test_reverted_entry_matches_commit() -> None:
    """No error when commit matches a reverted entry."""
    tracker = make_tracker([make_entry("a.el", "reverted")])
    log = ["abc [a.el] Upgrade pkg from v1 to v2"]
    assert validate_tracker_vs_git(tracker, log) == []


def test_non_upgrade_commit_ignored() -> None:
    """Non-upgrade commits are not flagged."""
    tracker = make_tracker([make_entry("a.el", "pending")])
    log = ["abc Fix typo in docs"]
    assert validate_tracker_vs_git(tracker, log) == []


def test_stale_data_matching_hash() -> None:
    """No error when graph hash matches derived data."""
    content = '{"test": true}'
    h = hashlib.sha256(content.encode()).hexdigest()
    data = DerivedDependencyData(
        schema_version=1, source_graph_hash=h,
        pkg_to_init={}, init_to_packages={},
        init_dep_graph={}, reverse_deps={}, sorted_files=[],
    )
    check_stale_derived_data(content, data)


def test_stale_data_mismatched_hash() -> None:
    """ValueError when graph hash differs from derived data."""
    data = DerivedDependencyData(
        schema_version=1, source_graph_hash="oldhash",
        pkg_to_init={}, init_to_packages={},
        init_dep_graph={}, reverse_deps={}, sorted_files=[],
    )
    with pytest.raises(ValueError, match=r"changed"):
        check_stale_derived_data('{"new": true}', data)
