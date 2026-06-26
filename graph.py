"""LangGraph workflow definition for incident investigation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph

from nodes.analyzer import analyzer_node
from nodes.deployment_collector import deployment_collector_node
from nodes.logs_collector import logs_collector_node
from nodes.metrics_collector import metrics_collector_node
from nodes.planner import planner_node
from nodes.reporter import reporter_node
from state import IncidentState

NodeFunction = Callable[[IncidentState], IncidentState]

NODE_SEQUENCE: tuple[str, ...] = (
    "planner",
    "metrics_collector",
    "logs_collector",
    "deployment_collector",
    "analyzer",
    "reporter",
)
"""Ordered workflow nodes for the current linear investigation graph."""

ORCHESTRATION_PATH: tuple[str, ...] = ("START", *NODE_SEQUENCE, "END")
"""Human-readable execution path for documentation and tests."""

NODE_REGISTRY: dict[str, NodeFunction] = {
    "planner": planner_node,
    "metrics_collector": metrics_collector_node,
    "logs_collector": logs_collector_node,
    "deployment_collector": deployment_collector_node,
    "analyzer": analyzer_node,
    "reporter": reporter_node,
}
"""Mapping from graph node names to node functions."""


def build_graph() -> Any:
    """Build and compile the current incident investigation graph."""

    graph = StateGraph(IncidentState)

    for node_name in NODE_SEQUENCE:
        graph.add_node(node_name, NODE_REGISTRY[node_name])

    graph.add_edge(START, "planner")
    for current_node, next_node in zip(NODE_SEQUENCE, NODE_SEQUENCE[1:]):
        graph.add_edge(current_node, next_node)
    graph.add_edge("reporter", END)

    return graph.compile()


def run_investigation(incident: str) -> IncidentState:
    """Run the graph for a single incident description."""

    app = build_graph()
    return app.invoke({"incident": incident})
