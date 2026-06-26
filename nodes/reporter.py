"""Reporting node for the incident workflow."""

from __future__ import annotations

from state import IncidentState


def reporter_node(state: IncidentState) -> IncidentState:
    """Generate a concise RCA draft from the current investigation state."""

    evidence_lines = [
        f"- {item['source']}: {item['summary']}" for item in state.get("evidence", [])
    ]
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "- No evidence collected."

    report = "\n".join(
        [
            "# Root Cause Analysis Draft",
            "",
            f"Incident: {state.get('incident', 'unspecified incident')}",
            "",
            "Hypothesis:",
            state.get("hypothesis", "No hypothesis generated."),
            "",
            "Reasoning:",
            state.get("reasoning", "No reasoning generated."),
            "",
            f"Confidence: {state.get('confidence', 0.0):.2f}",
            "",
            "Evidence:",
            evidence_text,
        ]
    )

    return {"report": report}
