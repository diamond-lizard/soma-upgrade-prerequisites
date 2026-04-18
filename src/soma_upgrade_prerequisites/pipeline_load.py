#!/usr/bin/env python3
# Pipeline step: load and parse the dependency graph JSON.
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from pydantic import ValidationError

from .constants import ReportSection
from .models import DependencyGraph

if TYPE_CHECKING:
    from .config import PipelineConfig
    from .protocols import FileSystem, GitClient


class GraphResult(NamedTuple):
    """Result of loading and parsing the dependency graph."""

    graph_data: DependencyGraph
    graph_content: str
    starting_commit: str


def load_and_parse_graph(
    fs: FileSystem,
    git: GitClient,
    config: PipelineConfig,
    sections: list[ReportSection],
) -> GraphResult:
    """Load graph JSON, parse it, and get the starting commit.

    Appends FAIL sections and raises PipelineStopError on errors.
    """
    from .pipeline import PipelineStopError

    try:
        content = fs.read_file(config.graph_json_path)
    except FileNotFoundError:
        sections.append(ReportSection(
            "Graph JSON", "FAIL",
            f"File not found: {config.graph_json_path}",
        ))
        raise PipelineStopError from None
    try:
        graph_data = DependencyGraph.model_validate_json(content)
    except ValidationError as exc:
        sections.append(ReportSection(
            "Graph JSON", "FAIL", f"Invalid JSON: {exc}",
        ))
        raise PipelineStopError from None
    try:
        commit = git.get_commit_hash(config.branch)
    except ValueError as exc:
        sections.append(ReportSection(
            "Git", "FAIL", str(exc),
        ))
        raise PipelineStopError from None
    return GraphResult(graph_data, content, commit)
