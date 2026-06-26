"""Planner node for the initial investigation workflow."""

from __future__ import annotations

from state import IncidentState


def planner_node(state: IncidentState) -> IncidentState:
    """Start the investigation and initialize shared investigation state."""

    incident = state.get("incident", "").strip()
    if not incident:
        incident = "unspecified incident"

    return {
        "incident": incident,
        "metrics": {},
        "logs": [],
        "deployments": [],
        "kubernetes": [],
        "evidence": [],
        "hypothesis": "",
        "confidence": 0.0,
        "reasoning": "",
        "investigation_attempts": 0,
        "report": "Investigation started.",
    }
