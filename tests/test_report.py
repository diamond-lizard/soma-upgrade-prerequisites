#!/usr/bin/env python3
# Tests for report formatting functions.
from __future__ import annotations

import click

from soma_upgrade_prerequisites.constants import ReportSection
from soma_upgrade_prerequisites.report import (
    build_generate_report,
    format_section,
)


def test_format_section_pass() -> None:
    """PASS section has correct format."""
    result = click.unstyle(format_section("Test", "PASS", "all good"))
    assert result.startswith("=== Test === PASS")
    assert "    all good" in result


def test_format_section_warn() -> None:
    """WARN section has correct format."""
    result = click.unstyle(format_section("Test", "WARN", "warning"))
    assert "WARN" in result


def test_format_section_fail() -> None:
    """FAIL section has correct format."""
    result = click.unstyle(format_section("Test", "FAIL", "error"))
    assert "FAIL" in result


def test_format_section_info() -> None:
    """INFO section has correct format."""
    result = click.unstyle(format_section("Test", "INFO", "info"))
    assert "INFO" in result


def test_format_section_empty_detail() -> None:
    """Empty detail returns only header line."""
    result = click.unstyle(format_section("Test", "PASS", ""))
    assert result == "=== Test === PASS"


def test_build_generate_report_joins_sections() -> None:
    """Joins multiple sections with blank lines."""
    sections = [
        ReportSection("A", "PASS", "ok"),
        ReportSection("B", "INFO", "info"),
    ]
    report, code = build_generate_report(sections)
    plain = click.unstyle(report)
    assert "=== A === PASS" in plain
    assert "=== B === INFO" in plain
    assert code == 0


def test_build_generate_report_fail_exit_code() -> None:
    """Exit code is 1 when any section has FAIL level."""
    sections = [
        ReportSection("A", "PASS", ""),
        ReportSection("B", "FAIL", "error"),
    ]
    _, code = build_generate_report(sections)
    assert code == 1
