#!/usr/bin/env python3
# Tests for tracker_io read/write functions.
from __future__ import annotations

import pytest
from pydantic import ValidationError

from soma_upgrade_prerequisites.tracker_io import read_tracker, write_tracker
from tests.fakes import InMemoryFileSystem
from tests.tracker_test_helpers import make_tracker


def test_read_tracker_missing_file() -> None:
    """read_tracker returns None for a non-existent file."""
    fs = InMemoryFileSystem()
    assert read_tracker(fs, "missing.json") is None


def test_read_tracker_malformed_json() -> None:
    """read_tracker raises ValidationError on malformed JSON."""
    fs = InMemoryFileSystem({"t.json": "not json"})
    with pytest.raises(ValidationError):
        read_tracker(fs, "t.json")


def test_read_tracker_version_mismatch() -> None:
    """read_tracker raises ValueError on schema version mismatch."""
    bad_tracker = (
        '{"schema_version": 999, "starting_commit": "x",'
        ' "generated_at": "t", "status_definitions": {},'
        ' "entries": []}'
    )
    fs = InMemoryFileSystem({"t.json": bad_tracker})
    with pytest.raises(ValueError, match=r"re-run"):
        read_tracker(fs, "t.json")


def test_write_tracker_backup() -> None:
    """write_tracker backs up existing file when backup=True."""
    fs = InMemoryFileSystem({"t.json": "old content"})
    tracker = make_tracker([])
    write_tracker(fs, "t.json", tracker, backup=True)
    assert fs.file_exists("t.json.bak")
    assert fs.read_file("t.json.bak") == "old content"
    assert "schema_version" in fs.read_file("t.json")
