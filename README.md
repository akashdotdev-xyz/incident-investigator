# AI Incident Investigation Agent

Production-inspired incident investigation workflow built with LangGraph,
FastAPI, Pydantic, and pytest.

The project evolves incrementally. Each phase must compile, run, and remain
independently testable before the next phase adds more behavior.

## Phase 1: Project Setup

### What Problem This Phase Solves

Before adding LLMs or real infrastructure integrations, the project needs a
stable shape:

- `app.py` owns the API and local command-line entrypoint.
- `graph.py` owns LangGraph orchestration.
- `state.py` defines the data that moves through the graph.
- `nodes/` contains single-responsibility workflow steps.
- `tools/` will contain infrastructure adapters.
- `prompts/` will contain LLM prompts when they are introduced.
- `tests/` verifies each phase.
- `config.py` loads runtime configuration from environment variables.

This separation keeps orchestration, IO, state, and business behavior from
becoming tangled as the workflow grows.

### Why Python Alone Is Insufficient

Plain Python functions are enough for a linear prototype:

```python
state = planner(state)
state = reporter(state)
```

That breaks down once the workflow needs conditional routing, loops,
checkpointing, streaming, human approval, and multi-agent supervision. Those
features require explicit workflow structure and inspectable state transitions.

### How LangGraph Helps

LangGraph lets us model the investigation as a stateful graph:

```text
START -> planner -> END
```

Each node receives the current state and returns a partial update. LangGraph
merges those updates and passes the new state to the next node.

### Tradeoffs

LangGraph adds an orchestration layer, so the initial code is slightly more
structured than a simple script. The tradeoff is useful because later phases can
add routing, cycles, checkpoints, and streaming without rewriting the project.

### Production Use Cases

The same graph structure maps well to real SRE workflows:

- collect metrics, logs, deployments, and Kubernetes evidence
- branch based on confidence
- pause for human approval
- resume after a crash
- stream progress to an API client
- trace behavior in LangSmith

## Phase 2: Minimal LangGraph Workflow

Current workflow:

```text
Incident -> Planner -> END
```

The planner does not call an LLM yet. It returns:

```text
Investigation started.
```

This proves the state, node, edge, and graph execution path works before adding
investigation complexity.

## Phase 3: Shared State

### What Problem This Phase Solves

An investigation produces many different kinds of data: incident description,
metrics, logs, deployments, evidence, hypotheses, confidence, and a final
report. Passing each value as a separate argument between functions does not
scale once the workflow branches or loops.

Graph state gives every node one shared contract:

```python
def node(state: IncidentState) -> IncidentState:
    return {"evidence": [...]}  # partial update
```

### Why Python Alone Is Insufficient

A normal mutable dictionary works for a short script, but it makes workflow
behavior implicit. Any function can mutate any key at any time, which makes
retries, tests, and recovery harder.

LangGraph encourages nodes to return updates instead of modifying the input in
place. That makes each step easier to test and makes state transitions visible.

### How LangGraph Solves It

`IncidentState` is a `TypedDict` that defines the shared state shape:

- `incident`
- `metrics`
- `logs`
- `deployments`
- `evidence`
- `hypothesis`
- `confidence`
- `report`

Each node receives the current state and returns a partial update. LangGraph
merges that update into the next state before following the next edge.

### Tradeoffs

Typed state requires upfront modeling. The benefit is that later phases can add
collectors, analyzers, conditional routes, checkpoints, and reports without
changing how data moves through the graph.

### Production Use Cases

Shared state is the backbone for:

- resuming an investigation after a worker restart
- showing partial progress to an API client
- auditing what evidence led to a hypothesis
- routing based on confidence or missing evidence
- handing state from one specialist agent to another

## Phase 4: Investigation Nodes

### What Problem This Phase Solves

An incident investigation has distinct responsibilities:

- plan the investigation
- collect metrics
- collect logs
- collect deployment data
- analyze the evidence
- report the result

Keeping these responsibilities in separate nodes prevents one large function
from becoming the whole system.

### Why Python Alone Is Insufficient

Python functions can separate code, but they do not describe workflow
execution. The order, state passing, retries, streaming, and future branching
still have to be managed manually.

LangGraph nodes make each step part of an explicit workflow. The node remains a
plain Python function, but the graph owns when it runs and how its returned
state update moves forward.

### How LangGraph Solves It

The current graph is linear:

```text
START
  -> planner
  -> metrics_collector
  -> logs_collector
  -> deployment_collector
  -> analyzer
  -> reporter
  -> END
```

Each node has one responsibility and returns only the keys it owns. Collectors
append evidence immutably by returning a new evidence list:

```python
return {
    "metrics": metrics,
    "evidence": [*state.get("evidence", []), new_item],
}
```

### Tradeoffs

More nodes means more files and tests. The benefit is that each investigation
step can be replaced independently later. In Phase 5, the collectors will call a
tool layer instead of keeping fake data inside the node.

### Production Use Cases

This structure maps to real incident systems where each node may call a
different backend:

- metrics from Prometheus or CloudWatch
- logs from ElasticSearch or CloudWatch Logs
- deployments from GitHub, Argo CD, or Kubernetes
- analysis from an LLM or a deterministic rules engine
- reporting to an API, Slack, or an RCA document

## Phase 5: Fake Investigation Tools

### What Problem This Phase Solves

Collector nodes should orchestrate investigation steps. They should not know the
details of where metrics, logs, or deployments come from.

This phase introduces a tool layer:

- `tools/metrics_tool.py`
- `tools/logs_tool.py`
- `tools/deployment_tool.py`

The tools still return deterministic fake data, but the boundary now looks like
a production integration point.

### Why Python Alone Is Insufficient

Plain Python helper functions can hide fake data, but without a workflow
boundary the same code often grows into mixed orchestration and IO. The node
starts making decisions, formatting evidence, querying services, and handling
tool-specific details all at once.

LangGraph keeps the node as the workflow unit. The tool is just the data access
adapter used by that node.

### How LangGraph Solves It

The graph still runs the same nodes:

```text
metrics_collector -> logs_collector -> deployment_collector
```

But each collector now calls a tool:

```python
metrics = get_service_metrics("checkout-service")
logs = search_service_logs("checkout-service")
deployments = get_recent_deployments("checkout-service")
```

State shape and graph routing do not change. Only the source of collected data
changes.

### Tradeoffs

The tool layer adds more files. The benefit is replaceability: Phase 19 can swap
fake tools for Prometheus, CloudWatch, ElasticSearch, GitHub, `kubectl`, or
Docker while keeping the graph and nodes mostly unchanged.

### Production Use Cases

Tool boundaries make it easier to add:

- retries and timeouts around external systems
- authentication per backend
- mock tools in tests
- provider-specific clients behind stable interfaces
- audit logs for every external observation

## Phase 6: Graph Orchestration

### What Problem This Phase Solves

The investigation now has multiple nodes. The system needs an explicit
definition of execution order:

```text
Planner
  -> Metrics
  -> Logs
  -> Deployments
  -> Analyzer
  -> Reporter
```

Without an orchestration layer, that order would live inside nested function
calls or a long procedural script.

### Why Python Alone Is Insufficient

Python can execute functions in sequence:

```python
state = planner(state)
state = metrics_collector(state)
state = logs_collector(state)
```

That is acceptable for a straight line, but it does not scale cleanly to
conditional routing, cycles, streaming, checkpointing, or human approval. The
workflow rules become mixed with business logic.

### How LangGraph Solves It

LangGraph separates workflow structure from node behavior:

- `START` is the reserved graph entrypoint.
- `END` is the reserved terminal point.
- Nodes are named workflow steps.
- Edges declare which node runs next.
- State is passed from node to node and merged after every update.

The current graph is:

```text
START
  -> planner
  -> metrics_collector
  -> logs_collector
  -> deployment_collector
  -> analyzer
  -> reporter
  -> END
```

In code, the node order is exposed as `NODE_SEQUENCE` and the readable path is
exposed as `ORCHESTRATION_PATH`. This makes the topology testable instead of
being hidden inside graph construction.

### State Propagation

Execution begins with:

```python
{"incident": "checkout latency spike"}
```

The planner initializes the shared state. Each collector adds its own evidence.
The analyzer reads the collected state and writes `hypothesis` and
`confidence`. The reporter reads the full state and writes the final RCA draft.

### Tradeoffs

The graph is more explicit than a plain script. The benefit is that future
phases can add conditional edges and loops by changing graph routing, not by
rewriting every node.

### Production Use Cases

Explicit orchestration is useful for:

- tracing which investigation step ran
- streaming node progress to a client
- retrying or timing out individual nodes
- inserting human approval between nodes
- replacing a linear edge with conditional routing
- checkpointing state after every step

## Installation

Python 3.12+ is recommended.

Using `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Using `pip`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the sample environment file if needed:

```bash
cp .env.example .env
```

No API key is required for the current phase.

## Run Locally

Command line:

```bash
python app.py "checkout latency spike"
```

Expected output:

```text
# Root Cause Analysis Draft
```

API:

```bash
uvicorn app:app --reload
```

Then call:

```bash
curl -X POST http://127.0.0.1:8000/investigate \
  -H "Content-Type: application/json" \
  -d '{"incident":"checkout latency spike"}'
```

Expected response:

```json
{
  "incident": "checkout latency spike",
  "metrics": {
    "latency_ms": 1250.0,
    "cpu_percent": 82.5,
    "memory_percent": 76.0
  },
  "logs": [
    {
      "source": "checkout-service",
      "message": "Timeout while calling payment-service."
    }
  ],
  "deployments": [
    {
      "service": "checkout-service",
      "version": "2026.06.26-1",
      "status": "deployed 12 minutes before incident"
    }
  ],
  "evidence": [
    {
      "source": "metrics",
      "summary": "Latency is elevated at 1250 ms while CPU is high at 82.5%."
    }
  ],
  "hypothesis": "The checkout-service deployment likely introduced a regression that increased latency and triggered downstream payment timeouts.",
  "confidence": 0.7,
  "report": "# Root Cause Analysis Draft\n..."
}
```

## Test

```bash
pytest
```

## Roadmap

The next phase replaces the deterministic analyzer with an OpenAI-backed SRE
analysis prompt that generates the hypothesis, confidence, and reasoning.
