"""Deployment collection node for the incident workflow."""

from __future__ import annotations

from state import EvidenceItem, IncidentState
from tools.deployment_tool import get_recent_deployments


def deployment_collector_node(state: IncidentState) -> IncidentState:
    """Collect deployment events for the current incident."""

    deployments = get_recent_deployments("checkout-service")
    evidence: list[EvidenceItem] = [
        *state.get("evidence", []),
        {
            "source": "deployments",
            "summary": "Checkout-service changed shortly before the incident.",
        },
    ]

    return {
        "deployments": deployments,
        "evidence": evidence,
    }
