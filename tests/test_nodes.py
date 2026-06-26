"""Unit tests for investigation nodes."""

from __future__ import annotations

from nodes import analyzer
from nodes.analyzer import AnalysisResult, analyzer_node, deterministic_analysis
from nodes.deployment_collector import deployment_collector_node
from nodes.kubernetes_collector import kubernetes_collector_node
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


def test_kubernetes_collector_adds_runtime_evidence() -> None:
    """The Kubernetes node should append runtime evidence and increment attempts."""

    result = kubernetes_collector_node(
        {
            "investigation_attempts": 0,
            "evidence": [
                {
                    "source": "metrics",
                    "summary": "Latency is elevated.",
                }
            ]
        }
    )

    assert [item["source"] for item in result["evidence"]] == [
        "metrics",
        "kubernetes",
    ]
    assert result["kubernetes"][1]["signal"] == "Previous container state was CrashLoopBackOff."
    assert result["kubernetes"][2]["signal"] == "Last termination reason was OOMKilled."
    assert result["investigation_attempts"] == 1


def test_analyzer_falls_back_to_deterministic_analysis(monkeypatch) -> None:
    """The analyzer should remain runnable without an OpenAI API key."""

    class TestSettings:
        openai_api_key = None
        openai_model = "test-model"

    monkeypatch.setattr(analyzer, "load_settings", lambda: TestSettings())

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
    assert "Latency is above 1000 ms" in result["reasoning"]


def test_analyzer_uses_openai_when_api_key_is_configured(monkeypatch) -> None:
    """The analyzer should call the OpenAI path when credentials exist."""

    class TestSettings:
        openai_api_key = "test-key"
        openai_model = "test-model"

    def fake_openai_analysis(state: IncidentState, model: str) -> IncidentState:
        assert model == "test-model"
        assert state["incident"] == "checkout latency spike"
        return {
            "hypothesis": "LLM hypothesis",
            "confidence": 0.82,
            "reasoning": "LLM reasoning",
        }

    monkeypatch.setattr(analyzer, "load_settings", lambda: TestSettings())
    monkeypatch.setattr(analyzer, "_openai_analysis", fake_openai_analysis)

    result = analyzer_node({"incident": "checkout latency spike"})

    assert result == {
        "hypothesis": "LLM hypothesis",
        "confidence": 0.82,
        "reasoning": "LLM reasoning",
    }


def test_deterministic_analysis_generates_hypothesis_from_collected_state() -> None:
    """The local analyzer should produce a deterministic hypothesis."""

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

    result = deterministic_analysis(state)

    assert "checkout-service deployment" in result["hypothesis"]
    assert result["confidence"] == 0.7
    assert "downstream payment timeouts" in result["reasoning"]


def test_deterministic_analysis_raises_confidence_with_kubernetes_evidence() -> None:
    """Kubernetes runtime evidence should strengthen the local analysis."""

    state: IncidentState = {
        "metrics": {"latency_ms": 1250.0},
        "deployments": [
            {
                "service": "checkout-service",
                "version": "2026.06.26-1",
                "status": "deployed 12 minutes before incident",
            }
        ],
        "kubernetes": [
            {
                "namespace": "production",
                "pod": "checkout-service-7d9f4c8f9b-x2k4m",
                "signal": "Last termination reason was OOMKilled.",
            }
        ],
    }

    result = deterministic_analysis(state)

    assert "memory regression" in result["hypothesis"]
    assert result["confidence"] == 0.85
    assert "OOMKilled termination" in result["reasoning"]


def test_analysis_result_validates_confidence_range() -> None:
    """LLM output should be constrained to a valid confidence range."""

    result = AnalysisResult(
        hypothesis="Deployment regression.",
        confidence=0.5,
        reasoning="Deployment and latency are correlated.",
    )

    assert result.confidence == 0.5


def test_reporter_generates_rca_draft() -> None:
    """The reporter should turn state into a readable RCA draft."""

    state: IncidentState = {
        "incident": "checkout latency spike",
        "hypothesis": "Checkout deployment regression.",
        "confidence": 0.7,
        "reasoning": "Latency increased after deployment.",
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
    assert "Latency increased after deployment." in result["report"]
    assert "Latency is elevated." in result["report"]
