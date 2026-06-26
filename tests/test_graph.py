"""Tests for the LangGraph investigation workflow."""

from __future__ import annotations

from graph import (
    CONFIDENCE_THRESHOLD,
    MAX_INVESTIGATION_ATTEMPTS,
    NODE_SEQUENCE,
    ORCHESTRATION_PATH,
    route_after_analysis,
    run_investigation,
)
from nodes import analyzer


class NoOpenAISettings:
    """Settings fixture that forces deterministic analysis in graph tests."""

    openai_api_key = None
    openai_model = "test-model"


def test_graph_orchestration_path_is_explicit() -> None:
    """The current graph should expose its execution order as a contract."""

    assert ORCHESTRATION_PATH == (
        "START",
        "planner",
        "metrics_collector",
        "logs_collector",
        "deployment_collector",
        "analyzer",
        "confidence_route",
        "reporter | kubernetes_collector",
        "kubernetes_collector -> analyzer",
        "END",
    )
    assert "kubernetes_collector" in NODE_SEQUENCE
    assert CONFIDENCE_THRESHOLD == 0.8
    assert MAX_INVESTIGATION_ATTEMPTS == 2


def test_route_after_analysis_reports_when_confidence_is_high() -> None:
    """High-confidence analysis should go directly to reporting."""

    assert route_after_analysis({"confidence": 0.8}) == "reporter"


def test_route_after_analysis_collects_more_evidence_when_confidence_is_low() -> None:
    """Low-confidence analysis should collect more evidence before reporting."""

    assert route_after_analysis({"confidence": 0.79}) == "kubernetes_collector"


def test_route_after_analysis_reports_when_retry_limit_is_reached() -> None:
    """Low confidence should report once the bounded loop reaches its limit."""

    assert (
        route_after_analysis(
            {
                "confidence": 0.1,
                "investigation_attempts": MAX_INVESTIGATION_ATTEMPTS,
            }
        )
        == "reporter"
    )


def test_graph_preserves_incident(monkeypatch) -> None:
    """The graph should preserve the incident across all nodes."""

    monkeypatch.setattr(analyzer, "load_settings", lambda: NoOpenAISettings())

    result = run_investigation("checkout latency spike")

    assert result["incident"] == "checkout latency spike"


def test_graph_collects_evidence_and_generates_report(monkeypatch) -> None:
    """The graph should collect evidence, route by confidence, and draft an RCA."""

    monkeypatch.setattr(analyzer, "load_settings", lambda: NoOpenAISettings())

    result = run_investigation("checkout latency spike")

    assert result["metrics"]["latency_ms"] == 1250.0
    assert len(result["logs"]) == 3
    assert result["deployments"][0]["service"] == "checkout-service"
    assert [item["source"] for item in result["evidence"]] == [
        "metrics",
        "logs",
        "deployments",
        "kubernetes",
    ]
    assert result["kubernetes"][2]["signal"] == "Last termination reason was OOMKilled."
    assert result["investigation_attempts"] == 1
    assert "memory regression" in result["hypothesis"]
    assert result["confidence"] == 0.85
    assert "OOMKilled termination" in result["reasoning"]
    assert "# Root Cause Analysis Draft" in result["report"]
