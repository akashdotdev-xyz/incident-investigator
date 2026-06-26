"""Analysis node for the incident workflow."""

from __future__ import annotations

from state import IncidentState


def analyzer_node(state: IncidentState) -> IncidentState:
    """Create a deterministic hypothesis from collected evidence."""

    metrics = state.get("metrics", {})
    deployments = state.get("deployments", [])

    latency = metrics.get("latency_ms", 0.0)
    changed_services = [
        deployment["service"]
        for deployment in deployments
        if deployment["status"] != "unchanged"
    ]

    if latency >= 1000.0 and "checkout-service" in changed_services:
        return {
            "hypothesis": (
                "The checkout-service deployment likely introduced a regression "
                "that increased latency and triggered downstream payment timeouts."
            ),
            "confidence": 0.7,
        }

    return {
        "hypothesis": "The incident needs more evidence before a likely cause can be named.",
        "confidence": 0.3,
    }
