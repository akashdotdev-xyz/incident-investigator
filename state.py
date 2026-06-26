"""State definitions for the incident investigation graph."""

from __future__ import annotations

from typing_extensions import TypedDict


class MetricsSnapshot(TypedDict, total=False):
    """Point-in-time application and infrastructure metrics."""

    latency_ms: float
    cpu_percent: float
    memory_percent: float


class LogFinding(TypedDict):
    """A notable log signal collected during an investigation."""

    source: str
    message: str


class DeploymentEvent(TypedDict):
    """A deployment event that may be relevant to the incident."""

    service: str
    version: str
    status: str


class EvidenceItem(TypedDict):
    """A normalized evidence item used by analysis and reporting nodes."""

    source: str
    summary: str


class IncidentState(TypedDict, total=False):
    """Shared graph state.

    Nodes should return partial updates instead of mutating this object in
    place. LangGraph merges those updates as the workflow moves across edges.
    """

    incident: str
    metrics: MetricsSnapshot
    logs: list[LogFinding]
    deployments: list[DeploymentEvent]
    evidence: list[EvidenceItem]
    hypothesis: str
    confidence: float
    report: str
