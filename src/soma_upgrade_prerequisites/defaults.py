#!/usr/bin/env python3
"""Default paths, schema versions, and file identity constants."""
# Default paths, schema versions, and file identity constants.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .constants import Status

# Default path to the dependency graph JSON file.
DEFAULT_GRAPH_JSON: str = (
    "~/.emacs.d/soma/inits-upgrades/soma-inits-dependency-graphs.json"
)

# Default directory containing upgrade-process.md and security-review.md files.
DEFAULT_UPGRADES_DIR: str = "~/.emacs.d/soma/inits-upgrades"

# Default directory containing init files.
DEFAULT_INITS_DIR: str = "~/.emacs.d/soma/inits"

# Default git branch for the upgrade campaign.
DEFAULT_BRANCH: str = "elpaca-upgrades"

# Default path to the progress tracker JSON file.
DEFAULT_TRACKER_PATH: str = (
    "~/.emacs.d/soma/inits-upgrades/upgrade-progress.json"
)

# Default path to the derived dependency data JSON file.
DEFAULT_DERIVED_DATA_PATH: str = (
    "~/.emacs.d/soma/inits-upgrades/derived-dependency-data.json"
)

# Default path to the git repository.
DEFAULT_REPO_PATH: str = "~/.emacs.d"

# Init file containing the elpaca package manager (must be upgraded first).
ELPACA_INIT_FILE: str = "init.el"

# Schema version for upgrade-progress.json; increment on structure changes.
TRACKER_SCHEMA_VERSION: int = 1

# Schema version for derived-dependency-data.json; increment on structure changes.
DERIVED_DATA_SCHEMA_VERSION: int = 1

# Human-readable definitions for each status (matching GUD-300).
STATUS_DEFINITIONS: dict[Status, str] = {
    "pending": "Not yet started",
    "in-progress": "Currently being upgraded",
    "upgraded": "Successfully upgraded, tested, and merged",
    "skipped": "User chose not to upgrade",
    "blocked": "Cannot upgrade due to unmet prerequisite; set only by cascade",
    "reverted": "Was upgraded but later reverted",
}
