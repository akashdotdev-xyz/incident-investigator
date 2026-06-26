"""Fake metrics tool for infrastructure investigation."""

from __future__ import annotations

from state import MetricsSnapshot


def get_service_metrics(service_name: str) -> MetricsSnapshot:
    """Return deterministic service metrics for local development.

    The service name is accepted now so the fake interface matches the future
    production adapter.
    """

    return {
        "latency_ms": 1250.0,
        "cpu_percent": 82.5,
        "memory_percent": 76.0,
    }
