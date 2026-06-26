"""Log collection node for the incident workflow."""

from __future__ import annotations

from state import EvidenceItem, IncidentState, LogFinding


def logs_collector_node(state: IncidentState) -> IncidentState:
    """Collect deterministic log findings for the current incident."""

    logs: list[LogFinding] = [
        {
            "source": "checkout-service",
            "message": "Timeout while calling payment-service.",
        },
        {
            "source": "payment-service",
            "message": "Database connection reset by peer.",
        },
        {
            "source": "checkout-service",
            "message": "Cache miss rate increased during checkout requests.",
        },
    ]
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
