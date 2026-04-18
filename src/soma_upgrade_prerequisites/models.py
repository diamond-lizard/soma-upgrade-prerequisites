#!/usr/bin/env python3
# Pydantic models for JSON data structures used by the tool.
# Provides runtime validation when loading JSON files.
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, RootModel

from .constants import Flag, OrphanClassification, Status

if TYPE_CHECKING:
    from collections.abc import Iterator


class PackageEntry(BaseModel):
    """A single package declaration within an init file."""

    package: str
    depends_on: list[str]
    repo_url: str
    min_emacs_version: str | None


class InitFileEntry(BaseModel):
    """An init file entry in the dependency graph."""

    packages: list[PackageEntry]
    depended_on_by: list[str]


class DependencyGraph(RootModel[dict[str, InitFileEntry]]):
    """Top-level dependency graph keyed by init file name."""

    def __getitem__(self, key: str) -> InitFileEntry:
        """Look up an init file entry by name."""
        return self.root[key]

    def keys(self) -> Iterator[str]:
        """Iterate over init file names."""
        return iter(self.root)

    def __len__(self) -> int:
        """Return the number of init file entries."""
        return len(self.root)

    def __contains__(self, key: object) -> bool:
        """Check if an init file name exists in the graph."""
        return key in self.root

    def items(self) -> Iterator[tuple[str, InitFileEntry]]:
        """Iterate over (name, entry) pairs."""
        return iter(self.root.items())


class TrackerEntry(BaseModel):
    """A single entry in the progress tracker."""

    order: int
    init_file: str
    package: str
    level: int
    flags: list[Flag]
    status: Status
    notes: str
    blocked_by: list[str] = []


class ProgressTracker(BaseModel):
    """The complete progress tracker JSON structure."""

    schema_version: int
    starting_commit: str
    generated_at: str
    status_definitions: dict[Status, str]
    entries: list[TrackerEntry]


class DerivedDependencyData(BaseModel):
    """Persisted dependency analysis results for offline use."""

    schema_version: int
    source_graph_hash: str
    pkg_to_init: dict[str, str]
    init_to_packages: dict[str, list[str]]
    init_dep_graph: dict[str, list[str]]
    reverse_deps: dict[str, list[str]]
    sorted_files: list[str]

class OrphanPackage(BaseModel):
    """A package referenced in depends_on but not declared in any init file."""

    package: str
    has_init_file: bool
    classification: OrphanClassification
