#!/usr/bin/env python3
# Tests for derived data read/write round-trip.
from __future__ import annotations

import pytest

from soma_upgrade_prerequisites.derived_data import (
    read_derived_data,
    write_derived_data,
)
from soma_upgrade_prerequisites.models import DerivedDependencyData
from tests.fakes import InMemoryFileSystem


def _make_derived_data() -> DerivedDependencyData:
    """Build a minimal DerivedDependencyData for testing."""
    return DerivedDependencyData(
        schema_version=1,
        source_graph_hash="abc123",
        pkg_to_init={"magit": "soma-magit-init.el"},
        init_to_packages={"soma-magit-init.el": ["magit"]},
        init_dep_graph={"soma-magit-init.el": []},
        reverse_deps={"soma-magit-init.el": []},
        sorted_files=["soma-magit-init.el"],
    )


def test_write_derived_data() -> None:
    """write_derived_data writes valid JSON to the fake filesystem."""
    fs = InMemoryFileSystem()
    data = _make_derived_data()
    write_derived_data(fs, "derived.json", data)
    assert "derived.json" in fs.files
    content = fs.read_file("derived.json")
    assert '"schema_version": 1' in content


def test_read_derived_data_round_trip() -> None:
    """read_derived_data returns a DerivedDependencyData from written file."""
    fs = InMemoryFileSystem()
    data = _make_derived_data()
    write_derived_data(fs, "derived.json", data)
    result = read_derived_data(fs, "derived.json")
    assert result is not None
    assert result.source_graph_hash == "abc123"
    assert result.pkg_to_init == {"magit": "soma-magit-init.el"}


def test_read_derived_data_missing_file() -> None:
    """read_derived_data returns None when file does not exist."""
    fs = InMemoryFileSystem()
    result = read_derived_data(fs, "missing.json")
    assert result is None


def test_read_derived_data_version_mismatch() -> None:
    """read_derived_data raises ValueError on schema version mismatch."""
    fs = InMemoryFileSystem()
    data = _make_derived_data()
    write_derived_data(fs, "derived.json", data)
    content = fs.read_file("derived.json")
    bad = content.replace('"schema_version": 1', '"schema_version": 999')
    fs.write_file("derived.json", bad)
    with pytest.raises(ValueError, match="re-run"):
        read_derived_data(fs, "derived.json")
