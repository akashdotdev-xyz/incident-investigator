"""Prompt construction for the SRE analyzer."""

from __future__ import annotations

import json

from state import IncidentState

SRE_SYSTEM_PROMPT = """You are an SRE engineer.

Analyze the incident evidence and identify the most likely root-cause
hypothesis. Be precise, avoid overclaiming, and set confidence between 0.0 and
1.0 based only on the supplied evidence.
"""


def build_analyzer_user_prompt(state: IncidentState) -> str:
    """Build the user prompt from the current investigation state."""

    payload = {
        "incident": state.get("incident", "unspecified incident"),
        "metrics": state.get("metrics", {}),
        "logs": state.get("logs", []),
        "deployments": state.get("deployments", []),
        "kubernetes": state.get("kubernetes", []),
        "evidence": state.get("evidence", []),
        "investigation_attempts": state.get("investigation_attempts", 0),
    }
    return (
        "Investigate this incident and return a structured RCA analysis.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
