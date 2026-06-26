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
Investigation started.
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
  "report": "Investigation started."
}
```

## Test

```bash
pytest
```

## Roadmap

The next phase expands `IncidentState` with metrics, logs, deployments,
evidence, hypothesis, confidence, and report fields. That will demonstrate why
shared graph state matters and how immutable node updates keep each step
predictable.
