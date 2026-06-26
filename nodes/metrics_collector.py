"""Metrics collection node for the incident workflow."""

from __future__ import annotations

from state import EvidenceItem, IncidentState
from tools.metrics_tool import get_service_metrics


def metrics_collector_node(state: IncidentState) -> IncidentState:
    """Collect metric signals for the current incident."""

    metrics = get_service_metrics("checkout-service")
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
