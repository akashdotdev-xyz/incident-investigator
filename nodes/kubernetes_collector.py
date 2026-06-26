"""Kubernetes evidence collection node for low-confidence investigations."""

from __future__ import annotations

from state import EvidenceItem, IncidentState, KubernetesFinding


def kubernetes_collector_node(state: IncidentState) -> IncidentState:
    """Collect Kubernetes pod signals and increment the investigation attempt."""

    findings: list[KubernetesFinding] = [
        {
            "namespace": "production",
            "pod": "checkout-service-7d9f4c8f9b-x2k4m",
            "signal": "Pod restarted 4 times in 10 minutes.",
        },
        {
            "namespace": "production",
            "pod": "checkout-service-7d9f4c8f9b-x2k4m",
            "signal": "Previous container state was CrashLoopBackOff.",
        },
        {
            "namespace": "production",
            "pod": "checkout-service-7d9f4c8f9b-x2k4m",
            "signal": "Last termination reason was OOMKilled.",
        },
    ]
    evidence: list[EvidenceItem] = [
        *state.get("evidence", []),
        {
            "source": "kubernetes",
            "summary": (
                "Checkout-service pods restarted repeatedly with CrashLoopBackOff "
                "and OOMKilled signals."
            ),
        },
    ]

    return {
        "kubernetes": findings,
        "evidence": evidence,
        "investigation_attempts": state.get("investigation_attempts", 0) + 1,
    }
