"""Fake logs tool for application investigation."""

from __future__ import annotations

from state import LogFinding


def search_service_logs(service_name: str) -> list[LogFinding]:
    """Return deterministic log findings for local development.

    The service name is accepted now so the fake interface matches the future
    production adapter.
    """

    return [
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
