# Nodex API Reference

This page documents the public API exposed by `nodex`.

## Agent

```python
Agent(name: str = "agent", debug: bool = False)
```

The main application object. It registers nodes, middleware, routes, and runs
the compiled LangGraph graph.

```python
from nodex import Agent

app = Agent(name="research-agent", debug=True)
```

### Agent.node

```python
@app.node(
    next: str = "end",
    retry: int = 0,
    on_fail: str = "raise",
    timeout: float | None = None,
    human_review: bool = False,
)
```

Registers a function as a graph node.

Parameters:

- `next`: next node name, or `"end"` to finish.
- `retry`: number of retry attempts before failure handling.
- `on_fail`: `"raise"`, `"skip"`, or a fallback node name.
- `timeout`: optional maximum node runtime in seconds. Defaults to `None`, so provider/model errors are not masked by a Nodex timeout unless you opt in.
- `human_review`: ask for terminal approval before continuing.

Node functions must return a non-empty dictionary.

### Agent.middleware

```python
@app.middleware
def logger(state, next_node):
    return next_node(state)
```

Registers middleware. Middleware receives the current `NodexState` and a
`next_node` callable.

### Agent.route

```python
@app.node()
@app.route(
    condition=lambda state: state.get("score", 0) > 7,
    if_true="publish",
    if_false="review",
)
def writer(state):
    return {"draft": "ready"}
```

Adds conditional routing metadata to a node.

## NodexState

`NodexState` wraps user data and keeps internal execution fields separate.

```python
state.get("query")
state.get("query", "default")
state.set("answer", "42")
state.update({"answer": "42"})
```

Protected internal keys:

- `_current_node`
- `_trace`
- `_retry_count`

## ExecutionTrace

Returned by `app.run(...)`.

Fields:

- `agent_name`
- `results`
- `total_duration`
- `total_cost`
- `total_tokens`
- `success`

## NodeResult

One result per executed node.

Fields:

- `node_name`
- `status`
- `output`
- `duration`
- `error`
- `retries`
- `tokens`
- `cost`

## Exceptions

Public exception types:

- `NodexError`
- `NodexNodeError`
- `NodexStateError`
- `NodexMiddlewareError`
- `NodexRouteError`
- `NodexConfigError`
- `NodexAuthError`
- `NodexTimeoutError`

## Testing helpers

```python
from nodex.testing import assert_node_output, make_state, test_node
```

Use `test_node` to run a single node without running the full graph.

```python
result = test_node(research, {"query": "AI trends"})
assert result.success
assert "research_results" in result.output
```
