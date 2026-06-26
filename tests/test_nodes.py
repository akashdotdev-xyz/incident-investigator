"""Unit tests for investigation nodes."""

from __future__ import annotations

from nodes.analyzer import analyzer_node
from nodes.deployment_collector import deployment_collector_node
from nodes.logs_collector import logs_collector_node
from nodes.metrics_collector import metrics_collector_node
from nodes.reporter import reporter_node
from state import IncidentState


def test_metrics_collector_adds_metrics_and_evidence() -> None:
    """The metrics node should update only metric-related state."""

    result = metrics_collector_node({"evidence": []})

    assert result["metrics"]["latency_ms"] == 1250.0
    assert result["evidence"][0]["source"] == "metrics"


def test_logs_collector_adds_log_findings_and_evidence() -> None:
    """The logs node should return deterministic log findings."""

    result = logs_collector_node({"evidence": []})

    assert len(result["logs"]) == 3
    assert result["logs"][0]["source"] == "checkout-service"
    assert result["evidence"][0]["source"] == "logs"


def test_deployment_collector_adds_deployments_and_evidence() -> None:
    """The deployment node should identify recent service changes."""

    result = deployment_collector_node({"evidence": []})

    assert result["deployments"][0]["service"] == "checkout-service"
    assert result["deployments"][1]["status"] == "unchanged"
    assert result["evidence"][0]["source"] == "deployments"


def test_analyzer_generates_hypothesis_from_collected_state() -> None:
    """The analyzer should produce a deterministic hypothesis and confidence."""

    state: IncidentState = {
        "metrics": {"latency_ms": 1250.0},
        "deployments": [
            {
                "service": "checkout-service",
                "version": "2026.06.26-1",
                "status": "deployed 12 minutes before incident",
            }
        ],
    }

    result = analyzer_node(state)

    assert "checkout-service deployment" in result["hypothesis"]
    assert result["confidence"] == 0.7


def test_reporter_generates_rca_draft() -> None:
    """The reporter should turn state into a readable RCA draft."""

    state: IncidentState = {
        "incident": "checkout latency spike",
        "hypothesis": "Checkout deployment regression.",
        "confidence": 0.7,
        "evidence": [
            {
                "source": "metrics",
                "summary": "Latency is elevated.",
            }
        ],
    }

    result = reporter_node(state)

    assert "# Root Cause Analysis Draft" in result["report"]
    assert "checkout latency spike" in result["report"]
    assert "Latency is elevated." in result["report"]
