"""Deployment collection node for the incident workflow."""

from __future__ import annotations

from state import DeploymentEvent, EvidenceItem, IncidentState


def deployment_collector_node(state: IncidentState) -> IncidentState:
    """Collect deterministic deployment events for the current incident."""

    deployments: list[DeploymentEvent] = [
        {
            "service": "checkout-service",
            "version": "2026.06.26-1",
            "status": "deployed 12 minutes before incident",
        },
        {
            "service": "payment-service",
            "version": "2026.06.25-4",
            "status": "unchanged",
        },
    ]
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
