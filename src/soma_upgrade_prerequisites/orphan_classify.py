#!/usr/bin/env python3
"""Classification logic for individual orphan packages."""
# Classification logic for individual orphan packages.
# Determines why a package has no declaring init file.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import DependencyGraph
    from .protocols import FileSystem

from .models import OrphanPackage


def classify_orphan(
    package: str,
    graph_data: DependencyGraph,
    fs: FileSystem,
    inits_dir: str,
    upgrades_dir: str,
) -> OrphanPackage:
    """Classify a single orphan package."""
    expected = f"soma-{package}-init.el"
    if expected in graph_data:
        return OrphanPackage(
            package=package, has_init_file=True,
            classification="misidentified",
        )
    init_file = _find_init_file(package, fs, inits_dir)
    if init_file is None:
        return OrphanPackage(
            package=package, has_init_file=False,
            classification="unresolvable",
        )
    if init_file in graph_data:
        return OrphanPackage(
            package=package, has_init_file=True,
            classification="missing-from-multi-package",
        )
    upgrade_path = f"{upgrades_dir}/{init_file}-upgrade-process.md"
    if not fs.file_exists(upgrade_path):
        return OrphanPackage(
            package=package, has_init_file=True,
            classification="dependency-not-to-be-upgraded",
        )
    return OrphanPackage(
        package=package, has_init_file=True,
        classification="unresolvable",
    )


def _find_init_file(
    package: str, fs: FileSystem, inits_dir: str,
) -> str | None:
    """Find init file on disk matching package with segment validation."""
    candidates = fs.list_files(inits_dir, f"soma-*{package}*-init.el")
    for name in candidates:
        if _segments_match(name, package):
            return name
    return None


def _segments_match(filename: str, package: str) -> bool:
    """Check package appears as contiguous segment subsequence."""
    stem = filename.removeprefix("soma-").removesuffix("-init.el")
    file_segs = stem.split("-")
    pkg_segs = package.split("-")
    for i in range(len(file_segs) - len(pkg_segs) + 1):
        if file_segs[i : i + len(pkg_segs)] == pkg_segs:
            return True
    return False
