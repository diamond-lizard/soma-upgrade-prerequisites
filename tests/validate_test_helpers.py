#!/usr/bin/env python3
"""Shared helpers for validation integration tests."""
from __future__ import annotations

import hashlib
import json

from soma_upgrade_prerequisites.config import ValidateConfig
from soma_upgrade_prerequisites.validate_runner import run_validation

from .fakes import InMemoryFileSystem


def run_with_fakes(tracker, git, sorted_files=None):
    """Run validation with fake FS and git; raises SystemExit on errors."""
    graph_content = "{}"
    graph_hash = hashlib.sha256(graph_content.encode()).hexdigest()
    files = sorted_files or [e.init_file for e in tracker.entries]
    derived = json.dumps({
        "schema_version": 1, "source_graph_hash": graph_hash,
        "pkg_to_init": {}, "init_to_packages": {},
        "init_dep_graph": {}, "reverse_deps": {},
        "sorted_files": files,
    })
    fs = InMemoryFileSystem({
        "/graph.json": graph_content,
        "/derived.json": derived,
    })
    config = ValidateConfig(
        tracker_path="/t.json", branch="main",
        graph_json_path="/graph.json", derived_data_path="/derived.json",
    )
    run_validation(fs, git, config, tracker)
