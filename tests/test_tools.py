"""Unit tests for fake investigation tools."""

from __future__ import annotations

from tools.deployment_tool import get_recent_deployments
from tools.logs_tool import search_service_logs
from tools.metrics_tool import get_service_metrics


def test_metrics_tool_returns_latency_cpu_and_memory() -> None:
    """The fake metrics tool should simulate high-level service health."""

    metrics = get_service_metrics("checkout-service")

    assert metrics == {
        "latency_ms": 1250.0,
        "cpu_percent": 82.5,
        "memory_percent": 76.0,
    }


def test_logs_tool_returns_relevant_log_signals() -> None:
    """The fake logs tool should simulate timeout, db reset, and cache miss logs."""

    logs = search_service_logs("checkout-service")

    assert [log["message"] for log in logs] == [
        "Timeout while calling payment-service.",
        "Database connection reset by peer.",
        "Cache miss rate increased during checkout requests.",
    ]


def test_deployment_tool_returns_recent_service_changes() -> None:
    """The fake deployment tool should simulate one changed service."""

    deployments = get_recent_deployments("checkout-service")

    assert deployments[0]["service"] == "checkout-service"
    assert deployments[0]["status"] == "deployed 12 minutes before incident"
    assert deployments[1]["service"] == "payment-service"
    assert deployments[1]["status"] == "unchanged"
