#!/usr/bin/env python3
# Frozen dataclasses for grouping CLI parameters into clean signatures.
# These are internal parameter objects, not JSON schemas (not Pydantic).
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Groups path and branch parameters for run_generate_pipeline."""

    graph_json_path: str
    upgrades_dir: str
    inits_dir: str
    branch: str
    tracker_path: str
    derived_data_path: str


@dataclass(frozen=True)
class ValidateConfig:
    """Groups path and branch parameters for the validate subcommand."""

    tracker_path: str
    branch: str
    graph_json_path: str
    derived_data_path: str
