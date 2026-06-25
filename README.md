# nodex

**The Express.js-style developer experience for LangGraph agents.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/nodex-ai.svg)](https://pypi.org/project/nodex-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/VamsiKrishna0101/Nodex/actions/workflows/test.yml/badge.svg)](https://github.com/VamsiKrishna0101/Nodex/actions)

Nodex is a thin layer on top of LangGraph that lets you build agents with
decorators, middleware, retries, fallbacks, tracing, and a small CLI.

It does not replace LangGraph. It removes the boilerplate around it.

## Why

LangGraph is powerful, but even a small agent can require manual state types,
node registration, edge wiring, retry handling, and debugging through several
layers of framework internals.

Nodex gives that workflow a smaller surface:

- Define graph steps with `@app.node`.
- Add cross-cutting behavior with `@app.middleware`.
- Route conditionally with `@app.route`.
- Run the graph with `app.run(...)` and get an `ExecutionTrace` back.
- Get a coloured terminal execution trace automatically — no setup needed.

## Install

```bash
pip install nodex-ai
```

Requires Python 3.11 or newer.

## Quickstart

```python
from nodex import Agent

app = Agent(name="hello-agent")


@app.node(next="writer")
def research(state):
    query = state.get("query", "LangGraph")
    return {"notes": f"Research notes about {query}"}


@app.node(next="end")
def writer(state):
    return {"final": state.get("notes").upper()}


if __name__ == "__main__":
    trace = app.run({"query": "agent frameworks"})
    print(trace.success)        # True
    print(trace.total_tokens)   # 0
```

Output:

```text
>  nodex running - hello-agent
--------------------------------------------------
OK  research       ->  0.002s  |  tokens: 0  |  $0.0000
OK  writer         ->  0.001s  |  tokens: 0  |  $0.0000
--------------------------------------------------
OK  Completed  |  0.023s  |  $0.0000  |  2 nodes  |  0 failed  |  tokens: 0
```

## LangGraph vs Nodex

**LangGraph (before):**

```python
from langgraph.graph import END, START, StateGraph

graph = StateGraph(dict)
graph.add_node("research", research)
graph.add_node("writer", writer)
graph.add_edge(START, "research")
graph.add_edge("research", "writer")
graph.add_edge("writer", END)
app = graph.compile()
```

**Nodex (after):**

```python
from nodex import Agent

app = Agent()


@app.node(next="writer")
def research(state):
    return {"notes": "research"}


@app.node(next="end")
def writer(state):
    return {"final": state.get("notes")}


app.run()
```

## Core API

### Agent

```python
from nodex import Agent

app = Agent(name="research-agent", debug=True)
```

`Agent` owns node registration, middleware registration, graph compilation, and
execution tracing. `app.run()` returns an [`ExecutionTrace`](#executiontrace).

### Nodes

```python
@app.node(next="writer", retry=2, on_fail="fallback_research")
def research(state):
    return {"research_results": "data"}
```

Node functions receive a `NodexState` object and must return a non-empty
dictionary. Internal keys such as `_trace` and `_retry_count` are protected.

| Parameter | Default | Description |
|---|---|---|
| `next` | `"end"` | Next node name, or `"end"` to finish. |
| `retry` | `0` | Retry attempts before failure handling. |
| `on_fail` | `"raise"` | `"raise"`, `"skip"`, or a fallback node name. |
| `timeout` | `None` | Optional max seconds for the node. `None` means no Nodex timeout unless you opt in. |
| `human_review` | `False` | Ask for terminal approval before continuing. |

### Middleware

```python
@app.middleware
def logger(state, next_node):
    print(f"running {state._current_node}")
    return next_node(state)
```

Middleware runs in registration order and wraps every node execution. Register
multiple middleware functions to build a chain.

### Conditional routing

```python
@app.node()
@app.route(
    condition=lambda state: state.get("confidence", 0) > 0.8,
    if_true="publish",
    if_false="review",
)
def writer(state):
    return {"draft": "ready", "confidence": 0.92}
```

### Human review

```python
@app.node(next="publish", human_review=True)
def review(state):
    return {"approved_content": state.get("draft")}
```

When `human_review=True`, Nodex asks for terminal approval before continuing.

### ExecutionTrace

`app.run()` returns an `ExecutionTrace` you can inspect after the run:

```python
trace = app.run({"query": "AI trends"})

print(trace.success)         # True
print(trace.total_duration)  # 0.48
print(trace.total_tokens)    # 237
print(trace.total_cost)      # 0.0005

for r in trace.results:
    print(r.node_name, r.status, r.duration)
```

## CLI

```bash
nodex new my-agent
cd my-agent
nodex dev agent:app
nodex run agent:app --input '{"query":"hello"}'
```

| Command | Description |
|---|---|
| `nodex new <name>` | Scaffold a starter agent project. |
| `nodex dev <target>` | Run in watch mode — restarts on file save. |
| `nodex run <target>` | One-shot execution with a full trace. |

The target format is `module:instance`, e.g. `agent:app`.

## Testing nodes

```python
from nodex.testing import assert_node_output, make_state, test_node


def test_research():
    result = test_node(research, {"query": "AI trends"})
    assert result.success
    assert "research_results" in result.output


def test_required_keys():
    assert_node_output(research, {"query": "AI trends"}, ["research_results"])


def test_with_custom_state():
    state = make_state({"query": "AI trends", "confidence": 0.9})
    result = test_node(writer, state)
    assert result.success
```

## Local development

```bash
pip install -e ".[dev]"
ruff check src tests
pytest
```

Current test suite: 58 tests, covering app, graph, CLI, decorators, middleware,
state, tracer, errors, and testing helpers.

## Documentation

The full docs site lives in `site/` and covers getting started, guides,
API reference, middleware patterns, CLI usage, and migration from LangGraph.

Serve it locally:

```bash
npm run dev
```

Then open `http://127.0.0.1:4173/`.

| Page | Path |
|---|---|
| Getting started | `/docs/getting-started.html` |
| Guide | `/docs/guide.html` |
| API reference | `/docs/api.html` |
| Middleware | `/docs/middleware.html` |
| CLI | `/docs/cli.html` |
| Migration from LangGraph | `/docs/migration.html` |

## Roadmap

- [x] Decorator-based node definition
- [x] Middleware engine
- [x] Retry and fallback handling
- [x] Terminal execution tracing
- [x] CLI scaffold/run/dev commands
- [x] Testing helpers
- [x] Multi-page docs site
- [ ] Provider-specific examples
- [ ] Dashboard or trace viewer

## License

MIT. See [LICENSE](LICENSE).
