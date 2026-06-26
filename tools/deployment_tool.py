"""Fake deployment tool for release investigation."""

from __future__ import annotations

from state import DeploymentEvent


def get_recent_deployments(service_name: str) -> list[DeploymentEvent]:
    """Return deterministic deployment events for local development.

    The service name is accepted now so the fake interface matches the future
    production adapter.
    """

    return [
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
