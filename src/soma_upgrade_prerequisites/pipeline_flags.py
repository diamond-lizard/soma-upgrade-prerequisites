#!/usr/bin/env python3
"""Flag assembly for tracker entries."""
# Flag assembly for tracker entries.
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .constants import Flag


def assemble_flags(
    warned: Mapping[str, Sequence[str]],
    high_risk: Mapping[str, Sequence[str]],
    multi_pkg: Mapping[str, int],
    new_deps: Sequence[str],
    upgrade_set: Sequence[str],
) -> dict[str, list[Flag]]:
    """Combine risk results into per-init-file flag lists."""
    result: dict[str, list[Flag]] = {}
    for init in upgrade_set:
        flags: list[Flag] = []
        if init in warned:
            flags.append("warned")
        if init in high_risk:
            flags.append("high-risk")
        if init in multi_pkg:
            flags.append("multi-pkg")
        if init in new_deps:
            flags.append("new-deps")
        if flags:
            result[init] = flags
    return result
