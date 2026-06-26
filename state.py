"""State definitions for the incident investigation graph."""

from __future__ import annotations

from typing_extensions import TypedDict


class IncidentState(TypedDict, total=False):
    """Shared graph state.

    Phase 1 keeps the state deliberately small. Later phases will extend this
    contract with metrics, logs, deployments, evidence, hypotheses, confidence,
    and the final RCA report.
    """

    incident: str
    report: str
