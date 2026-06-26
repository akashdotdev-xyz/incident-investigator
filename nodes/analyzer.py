"""Analysis node for the incident workflow."""

from __future__ import annotations

from pydantic import BaseModel, Field

from config import load_settings
from prompts.analyzer_prompt import SRE_SYSTEM_PROMPT, build_analyzer_user_prompt
from state import IncidentState


class AnalysisResult(BaseModel):
    """Structured analysis returned by the SRE analyzer."""

    hypothesis: str = Field(description="Most likely root-cause hypothesis.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence from 0.0 to 1.0.")
    reasoning: str = Field(description="Concise explanation for the hypothesis.")


def analyzer_node(state: IncidentState) -> IncidentState:
    """Analyze collected evidence with OpenAI when configured."""

    settings = load_settings()
    if settings.openai_api_key:
        return _openai_analysis(state, settings.openai_model)

    return deterministic_analysis(state)


def deterministic_analysis(state: IncidentState) -> IncidentState:
    """Create a deterministic local analysis when no LLM is configured."""

    metrics = state.get("metrics", {})
    deployments = state.get("deployments", [])
    kubernetes = state.get("kubernetes", [])

    latency = metrics.get("latency_ms", 0.0)
    changed_services = [
        deployment["service"]
        for deployment in deployments
        if deployment["status"] != "unchanged"
    ]

    if latency >= 1000.0 and "checkout-service" in changed_services and kubernetes:
        return {
            "hypothesis": (
                "The checkout-service deployment likely introduced a memory "
                "regression that caused pod restarts, CrashLoopBackOff, and "
                "downstream payment timeouts."
            ),
            "confidence": 0.85,
            "reasoning": (
                "Latency is above 1000 ms, checkout-service changed shortly before "
                "the incident, logs show downstream payment timeouts, and "
                "Kubernetes reports restarts with OOMKilled termination."
            ),
        }

    if latency >= 1000.0 and "checkout-service" in changed_services:
        return {
            "hypothesis": (
                "The checkout-service deployment likely introduced a regression "
                "that increased latency and triggered downstream payment timeouts."
            ),
            "confidence": 0.7,
            "reasoning": (
                "Latency is above 1000 ms, checkout-service changed shortly before "
                "the incident, and logs show downstream payment timeouts."
            ),
        }

    return {
        "hypothesis": "The incident needs more evidence before a likely cause can be named.",
        "confidence": 0.3,
        "reasoning": "The collected evidence does not contain a strong correlated signal.",
    }


def _openai_analysis(state: IncidentState, model: str) -> IncidentState:
    """Run the structured SRE analysis prompt with OpenAI."""

    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model=model, temperature=0)
    structured_llm = llm.with_structured_output(AnalysisResult)
    result = structured_llm.invoke(
        [
            ("system", SRE_SYSTEM_PROMPT),
            ("user", build_analyzer_user_prompt(state)),
        ]
    )

    if not isinstance(result, AnalysisResult):
        result = AnalysisResult.model_validate(result)

    return {
        "hypothesis": result.hypothesis,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
    }
