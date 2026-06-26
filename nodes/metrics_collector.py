"""Metrics collection node for the incident workflow."""

from __future__ import annotations

from state import EvidenceItem, IncidentState, MetricsSnapshot


def metrics_collector_node(state: IncidentState) -> IncidentState:
    """Collect deterministic metric signals for the current incident."""

    metrics: MetricsSnapshot = {
        "latency_ms": 1250.0,
        "cpu_percent": 82.5,
        "memory_percent": 76.0,
    }
    evidence: list[EvidenceItem] = [
        *state.get("evidence", []),
        {
            "source": "metrics",
            "summary": "Latency is elevated at 1250 ms while CPU is high at 82.5%.",
        },
    ]

    return {
        "metrics": metrics,
        "evidence": evidence,
    }
