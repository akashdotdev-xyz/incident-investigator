"""Tests for the LangGraph investigation workflow."""

from __future__ import annotations

from graph import NODE_SEQUENCE, ORCHESTRATION_PATH, run_investigation


def test_graph_orchestration_path_is_explicit() -> None:
    """The current graph should expose its execution order as a contract."""

    assert ORCHESTRATION_PATH == (
        "START",
        "planner",
        "metrics_collector",
        "logs_collector",
        "deployment_collector",
        "analyzer",
        "reporter",
        "END",
    )
    assert NODE_SEQUENCE == ORCHESTRATION_PATH[1:-1]


def test_graph_preserves_incident() -> None:
    """The graph should preserve the incident across all nodes."""

    result = run_investigation("checkout latency spike")

    assert result["incident"] == "checkout latency spike"


def test_graph_collects_evidence_and_generates_report() -> None:
    """The full Phase 4 graph should collect evidence and draft an RCA."""

    result = run_investigation("checkout latency spike")

    assert result["metrics"]["latency_ms"] == 1250.0
    assert len(result["logs"]) == 3
    assert result["deployments"][0]["service"] == "checkout-service"
    assert [item["source"] for item in result["evidence"]] == [
        "metrics",
        "logs",
        "deployments",
    ]
    assert "checkout-service deployment" in result["hypothesis"]
    assert result["confidence"] == 0.7
    assert "# Root Cause Analysis Draft" in result["report"]
