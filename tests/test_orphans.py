#!/usr/bin/env python3
# Tests for find_orphan_packages classification.
from __future__ import annotations

from soma_upgrade_prerequisites.orphan_detection import find_orphan_packages
from tests.fakes import InMemoryFileSystem
from tests.helpers import make_graph, pkg


def test_misidentified_orphan() -> None:
    """Orphan classified as misidentified when init file exists in graph."""
    graph = make_graph({
        "soma-evil-init.el": {
            "packages": [pkg("evil-collection", [])],
            "depended_on_by": [],
        },
        "soma-other-init.el": {
            "packages": [pkg("other", ["evil"])],
            "depended_on_by": [],
        },
    })
    pkg_to_init = {"evil-collection": "soma-evil-init.el", "other": "soma-other-init.el"}
    fs = InMemoryFileSystem()
    result = find_orphan_packages(graph, pkg_to_init, fs, "inits", "upgrades")
    assert len(result) == 1
    assert result[0].package == "evil"
    assert result[0].classification == "misidentified"


def test_dependency_not_to_be_upgraded() -> None:
    """Orphan on disk but not in graph and no upgrade-process.md."""
    graph = make_graph({
        "soma-a-init.el": {
            "packages": [pkg("a", ["extpkg"])],
            "depended_on_by": [],
        },
    })
    pkg_to_init = {"a": "soma-a-init.el"}
    fs = InMemoryFileSystem({
        "inits/soma-extpkg-init.el": "",
    })
    result = find_orphan_packages(graph, pkg_to_init, fs, "inits", "upgrades")
    assert len(result) == 1
    assert result[0].package == "extpkg"
    assert result[0].classification == "dependency-not-to-be-upgraded"


def test_missing_from_multi_package() -> None:
    """Orphan's init file is in graph but doesn't list this package."""
    graph = make_graph({
        "soma-multi-extra-init.el": {
            "packages": [pkg("pkg-a", [])],
            "depended_on_by": [],
        },
        "soma-user-init.el": {
            "packages": [pkg("user", ["extra"])],
            "depended_on_by": [],
        },
    })
    pkg_to_init = {"pkg-a": "soma-multi-extra-init.el", "user": "soma-user-init.el"}
    fs = InMemoryFileSystem({"inits/soma-multi-extra-init.el": ""})
    result = find_orphan_packages(graph, pkg_to_init, fs, "inits", "upgrades")
    orphan = next(o for o in result if o.package == "extra")
    assert orphan.classification == "missing-from-multi-package"


def test_unresolvable_orphan() -> None:
    """Orphan with no matching init file on disk."""
    graph = make_graph({
        "soma-a-init.el": {
            "packages": [pkg("a", ["mystery"])],
            "depended_on_by": [],
        },
    })
    pkg_to_init = {"a": "soma-a-init.el"}
    fs = InMemoryFileSystem()
    result = find_orphan_packages(graph, pkg_to_init, fs, "inits", "upgrades")
    assert len(result) == 1
    assert result[0].package == "mystery"
    assert result[0].classification == "unresolvable"


def test_segment_validation_no_false_match() -> None:
    """Package 'db' must not match 'soma-bbdb-init.el'."""
    graph = make_graph({
        "soma-a-init.el": {
            "packages": [pkg("a", ["db"])],
            "depended_on_by": [],
        },
    })
    pkg_to_init = {"a": "soma-a-init.el"}
    fs = InMemoryFileSystem({"inits/soma-bbdb-init.el": ""})
    result = find_orphan_packages(graph, pkg_to_init, fs, "inits", "upgrades")
    assert len(result) == 1
    assert result[0].classification == "unresolvable"
    assert result[0].has_init_file is False
