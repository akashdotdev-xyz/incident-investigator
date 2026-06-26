"""Tests for the minimal LangGraph workflow."""

from __future__ import annotations

from graph import run_investigation


def test_minimal_graph_starts_investigation() -> None:
    """The planner should start the investigation and preserve the incident."""

    result = run_investigation("checkout latency spike")

    assert result["incident"] == "checkout latency spike"
    assert result["report"] == "Investigation started."
