"""Planner node for the initial investigation workflow."""

from __future__ import annotations

from state import IncidentState


def planner_node(state: IncidentState) -> IncidentState:
    """Start the investigation and return the first state update."""

    incident = state.get("incident", "").strip()
    if not incident:
        incident = "unspecified incident"

    return {
        "incident": incident,
        "report": "Investigation started.",
    }
