#!/usr/bin/env python3
# Tests for cycle detection in dependency graphs.
from __future__ import annotations

from soma_upgrade_prerequisites.cycle_detection import detect_cycles


def test_acyclic_graph_returns_empty() -> None:
    """An acyclic graph has no cycles."""
    graph = {"a": ["b"], "b": ["c"], "c": []}
    assert detect_cycles(graph) == []


def test_two_node_cycle() -> None:
    """A simple A->B->A cycle is detected."""
    graph = {"a": ["b"], "b": ["a"]}
    cycles = detect_cycles(graph)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"a", "b"}


def test_three_node_cycle() -> None:
    """A->B->C->A cycle is detected."""
    graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    cycles = detect_cycles(graph)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"a", "b", "c"}


def test_cycle_with_acyclic_branch() -> None:
    """Only the cycle is reported, not the acyclic branch."""
    graph = {"a": ["b"], "b": ["a"], "c": ["a"], "d": []}
    cycles = detect_cycles(graph)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"a", "b"}


def test_no_edges_returns_empty() -> None:
    """A graph with no edges has no cycles."""
    graph = {"a": [], "b": [], "c": []}
    assert detect_cycles(graph) == []
