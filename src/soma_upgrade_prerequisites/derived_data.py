#!/usr/bin/env python3
"""Read and write operations for derived dependency data JSON."""
# Read and write operations for derived dependency data JSON.
from __future__ import annotations

from typing import TYPE_CHECKING

from .defaults import DERIVED_DATA_SCHEMA_VERSION
from .models import DerivedDependencyData

if TYPE_CHECKING:
    from .protocols import FileSystem


def write_derived_data(
    fs: FileSystem, path: str, data: DerivedDependencyData,
) -> None:
    """Serialize derived data as pretty-printed JSON and write to path."""
    fs.write_file(path, data.model_dump_json(indent=2))


def read_derived_data(
    fs: FileSystem, path: str,
) -> DerivedDependencyData | None:
    """Read and validate derived data JSON, or None if file missing.

    Raises ValueError if schema_version does not match.
    """
    if not fs.file_exists(path):
        return None
    content = fs.read_file(path)
    data = DerivedDependencyData.model_validate_json(content)
    if data.schema_version != DERIVED_DATA_SCHEMA_VERSION:
        msg = (
            f"Derived data schema version {data.schema_version} does not "
            f"match expected {DERIVED_DATA_SCHEMA_VERSION}. "
            "Please re-run `generate --write`."
        )
        raise ValueError(msg)
    return data
