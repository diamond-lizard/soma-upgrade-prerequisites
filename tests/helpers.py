#!/usr/bin/env python3
# Shared test helpers for constructing test data.
from __future__ import annotations

from soma_upgrade_prerequisites.models import DependencyGraph


def make_graph(data: dict[str, object]) -> DependencyGraph:
    """Build a DependencyGraph from a dict."""
    return DependencyGraph.model_validate(data)


def pkg(name: str, deps: list[str] | None = None) -> dict[str, object]:
    """Build a package entry dict."""
    return {
        "package": name,
        "depends_on": deps or [],
        "repo_url": "https://example.com",
        "min_emacs_version": None,
    }
