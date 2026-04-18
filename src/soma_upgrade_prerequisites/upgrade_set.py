#!/usr/bin/env python3
# Upgrade set identification and path-building helpers.
# Lists init files with upgrade instructions (the upgrade candidates).
from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protocols import FileSystem

UPGRADE_SUFFIX = "-upgrade-process.md"
SECURITY_SUFFIX = "-security-review.md"


def list_upgrade_files(fs: FileSystem, upgrades_dir: str) -> list[str]:
    """List upgrade-process.md files and return init file names.

    The returned list is the upgrade set -- init files with upgrade
    instructions that are candidates for upgrading.
    """
    files = fs.list_files(upgrades_dir, f"*{UPGRADE_SUFFIX}")
    return [f.removesuffix(UPGRADE_SUFFIX) for f in files]


def build_upgrade_path(upgrades_dir: str, init_file: str) -> str:
    """Build the path to an upgrade-process.md file."""
    return str(PurePosixPath(upgrades_dir) / f"{init_file}{UPGRADE_SUFFIX}")


def build_security_path(upgrades_dir: str, init_file: str) -> str:
    """Build the path to a security-review.md file."""
    return str(PurePosixPath(upgrades_dir) / f"{init_file}{SECURITY_SUFFIX}")
