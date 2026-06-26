"""Log collection node for the incident workflow."""

from __future__ import annotations

from state import EvidenceItem, IncidentState
from tools.logs_tool import search_service_logs


def logs_collector_node(state: IncidentState) -> IncidentState:
    """Collect log findings for the current incident."""

    logs = search_service_logs("checkout-service")
    evidence: list[EvidenceItem] = [
        *state.get("evidence", []),
        {
            "source": "logs",
            "summary": "Checkout requests show payment timeouts and database resets.",
        },
    ]

    return {
        "logs": logs,
        "evidence": evidence,
    }
