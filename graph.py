"""LangGraph workflow definition for incident investigation."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from nodes.analyzer import analyzer_node
from nodes.deployment_collector import deployment_collector_node
from nodes.logs_collector import logs_collector_node
from nodes.metrics_collector import metrics_collector_node
from nodes.planner import planner_node
from nodes.reporter import reporter_node
from state import IncidentState


def build_graph() -> Any:
    """Build and compile the current incident investigation graph."""

    graph = StateGraph(IncidentState)
    graph.add_node("planner", planner_node)
    graph.add_node("metrics_collector", metrics_collector_node)
    graph.add_node("logs_collector", logs_collector_node)
    graph.add_node("deployment_collector", deployment_collector_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("reporter", reporter_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "metrics_collector")
    graph.add_edge("metrics_collector", "logs_collector")
    graph.add_edge("logs_collector", "deployment_collector")
    graph.add_edge("deployment_collector", "analyzer")
    graph.add_edge("analyzer", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()


def run_investigation(incident: str) -> IncidentState:
    """Run the graph for a single incident description."""

    app = build_graph()
    return app.invoke({"incident": incident})
