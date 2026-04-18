#!/usr/bin/env python3
"""Detection of non-empty "New Dependencies" sections."""
# Detection of non-empty "New Dependencies" sections.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .protocols import FileSystem


def find_new_deps_files(
    fs: FileSystem,
    upgrades_dir: str,
    upgrade_set: Sequence[str],
) -> list[str]:
    """Identify init files with non-empty New Dependencies sections."""
    from .constants import NEW_DEPS_HEADER, NEW_DEPS_NONE_PATTERNS
    from .upgrade_set import build_upgrade_path

    return [
        init for init in upgrade_set
        if _has_new_deps(
            fs.read_file(build_upgrade_path(upgrades_dir, init)),
            NEW_DEPS_HEADER, NEW_DEPS_NONE_PATTERNS,
        )
    ]


def _has_new_deps(
    content: str, header: str, none_patterns: Sequence[str],
) -> bool:
    """Check whether the New Dependencies section has real content."""
    idx = content.find(header)
    if idx == -1:
        return False
    after = content[idx + len(header):]
    next_header = after.find("\n## ")
    section = after[:next_header] if next_header != -1 else after
    first_line = _first_nonempty_line(section)
    if first_line is None:
        return False
    cleaned = first_line.lstrip("*_").lower()
    return not any(cleaned.startswith(p) for p in none_patterns)


def _first_nonempty_line(text: str) -> str | None:
    """Return the first non-empty line, stripped, or None."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None
