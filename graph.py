"""LangGraph workflow definition for incident investigation."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from nodes.planner import planner_node
from state import IncidentState


def build_graph() -> Any:
    """Build and compile the current incident investigation graph."""

    graph = StateGraph(IncidentState)
    graph.add_node("planner", planner_node)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", END)
    return graph.compile()


def run_investigation(incident: str) -> IncidentState:
    """Run the graph for a single incident description."""

    app = build_graph()
    return app.invoke({"incident": incident})
