"""LangGraph workflow definition for incident investigation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from nodes.analyzer import analyzer_node
from nodes.deployment_collector import deployment_collector_node
from nodes.kubernetes_collector import kubernetes_collector_node
from nodes.logs_collector import logs_collector_node
from nodes.metrics_collector import metrics_collector_node
from nodes.planner import planner_node
from nodes.reporter import reporter_node
from state import IncidentState

NodeFunction = Callable[[IncidentState], IncidentState]
AnalyzerRoute = Literal["reporter", "kubernetes_collector"]

NODE_SEQUENCE: tuple[str, ...] = (
    "planner",
    "metrics_collector",
    "logs_collector",
    "deployment_collector",
    "analyzer",
    "kubernetes_collector",
    "reporter",
)
"""Workflow nodes registered in the current investigation graph."""

ORCHESTRATION_PATH: tuple[str, ...] = (
    "START",
    "planner",
    "metrics_collector",
    "logs_collector",
    "deployment_collector",
    "analyzer",
    "confidence_route",
    "reporter | kubernetes_collector",
    "kubernetes_collector -> analyzer",
    "END",
)
"""Human-readable execution path for documentation and tests."""

CONFIDENCE_THRESHOLD = 0.8
"""Minimum analyzer confidence required to report without extra evidence."""

MAX_INVESTIGATION_ATTEMPTS = 2
"""Maximum extra evidence collection attempts before reporting."""

NODE_REGISTRY: dict[str, NodeFunction] = {
    "planner": planner_node,
    "metrics_collector": metrics_collector_node,
    "logs_collector": logs_collector_node,
    "deployment_collector": deployment_collector_node,
    "analyzer": analyzer_node,
    "kubernetes_collector": kubernetes_collector_node,
    "reporter": reporter_node,
}
"""Mapping from graph node names to node functions."""


def route_after_analysis(state: IncidentState) -> AnalyzerRoute:
    """Choose the next node based on analyzer confidence."""

    if state.get("confidence", 0.0) >= CONFIDENCE_THRESHOLD:
        return "reporter"
    if state.get("investigation_attempts", 0) >= MAX_INVESTIGATION_ATTEMPTS:
        return "reporter"
    return "kubernetes_collector"


def build_graph() -> Any:
    """Build and compile the current incident investigation graph."""

    graph = StateGraph(IncidentState)

    for node_name in NODE_SEQUENCE:
        graph.add_node(node_name, NODE_REGISTRY[node_name])

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "metrics_collector")
    graph.add_edge("metrics_collector", "logs_collector")
    graph.add_edge("logs_collector", "deployment_collector")
    graph.add_edge("deployment_collector", "analyzer")
    graph.add_conditional_edges(
        "analyzer",
        route_after_analysis,
        {
            "reporter": "reporter",
            "kubernetes_collector": "kubernetes_collector",
        },
    )
    graph.add_edge("kubernetes_collector", "analyzer")
    graph.add_edge("reporter", END)

    return graph.compile()


def run_investigation(incident: str) -> IncidentState:
    """Run the graph for a single incident description."""

    app = build_graph()
    return app.invoke({"incident": incident})
