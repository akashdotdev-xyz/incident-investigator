"""FastAPI entrypoint and local CLI for the incident investigator."""

from __future__ import annotations

import argparse

import structlog
from fastapi import FastAPI
from pydantic import BaseModel, Field

from config import load_settings
from graph import run_investigation
from state import (
    DeploymentEvent,
    EvidenceItem,
    KubernetesFinding,
    LogFinding,
    MetricsSnapshot,
)


settings = load_settings()
logger = structlog.get_logger(__name__)

app = FastAPI(title="AI Incident Investigation Agent")


class InvestigationRequest(BaseModel):
    """Request body for starting an investigation."""

    incident: str = Field(min_length=1, description="Incident summary to investigate.")


class InvestigationResponse(BaseModel):
    """Response body for the current investigation graph state."""

    incident: str
    metrics: MetricsSnapshot
    logs: list[LogFinding]
    deployments: list[DeploymentEvent]
    kubernetes: list[KubernetesFinding]
    evidence: list[EvidenceItem]
    hypothesis: str
    confidence: float
    reasoning: str
    investigation_attempts: int
    report: str


@app.get("/health")
def health() -> dict[str, str]:
    """Return basic service health."""

    return {"status": "ok", "env": settings.app_env}


@app.post("/investigate", response_model=InvestigationResponse)
def investigate(request: InvestigationRequest) -> InvestigationResponse:
    """Run the investigation graph for an incident."""

    logger.info("investigation_started", incident=request.incident)
    result = run_investigation(request.incident)
    return InvestigationResponse(
        incident=result["incident"],
        metrics=result["metrics"],
        logs=result["logs"],
        deployments=result["deployments"],
        kubernetes=result["kubernetes"],
        evidence=result["evidence"],
        hypothesis=result["hypothesis"],
        confidence=result["confidence"],
        reasoning=result["reasoning"],
        investigation_attempts=result["investigation_attempts"],
        report=result["report"],
    )


def main() -> None:
    """Run the graph from the command line for local verification."""

    parser = argparse.ArgumentParser(description="Run a minimal incident investigation.")
    parser.add_argument("incident", nargs="?", default="checkout latency spike")
    args = parser.parse_args()

    result = run_investigation(args.incident)
    print(result["report"])


if __name__ == "__main__":
    main()
