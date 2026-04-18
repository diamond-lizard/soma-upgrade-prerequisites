#!/usr/bin/env python3
# Tests for validation check functions.
from __future__ import annotations

from soma_upgrade_prerequisites.validation import (
    validate_mapping_completeness,
)
from tests.helpers import make_graph, pkg


def test_mapping_complete() -> None:
    """Returns empty list when all packages are mapped."""
    graph = make_graph({
        "a.el": {"packages": [pkg("x")], "depended_on_by": []},
    })
    assert validate_mapping_completeness(graph, {"x": "a.el"}) == []


def test_mapping_missing_package() -> None:
    """Returns errors when packages are missing from the mapping."""
    graph = make_graph({
        "a.el": {"packages": [pkg("x")], "depended_on_by": []},
    })
    errors = validate_mapping_completeness(graph, {})
    assert len(errors) == 1
    assert "x" in errors[0]
