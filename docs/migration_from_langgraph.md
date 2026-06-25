# Migration From LangGraph To Nodex

This guide shows how to move a simple LangGraph workflow to Nodex.

## Before: manual LangGraph wiring

```python
from langgraph.graph import END, START, StateGraph


def research(state):
    return {"notes": "research"}


def writer(state):
    return {"final": state["notes"]}


graph = StateGraph(dict)
graph.add_node("research", research)
graph.add_node("writer", writer)
graph.add_edge(START, "research")
graph.add_edge("research", "writer")
graph.add_edge("writer", END)
app = graph.compile()

app.invoke({"query": "agent frameworks"})
```

## After: Nodex decorators

```python
from nodex import Agent

app = Agent(name="migration-example")


@app.node(next="writer")
def research(state):
    return {"notes": "research"}


@app.node(next="end")
def writer(state):
    return {"final": state.get("notes")}


app.run({"query": "agent frameworks"})
```

## Step-by-step migration

1. Create an `Agent`.
2. Convert each LangGraph node function to `@app.node`.
3. Move direct edges into the `next` argument.
4. Replace the final `END` edge with `next="end"`.
5. Replace `graph.compile().invoke(...)` with `app.run(...)`.

## Conditional routing

LangGraph conditional edges become `@app.route`.

```python
@app.node()
@app.route(
    condition=lambda state: state.get("score", 0) >= 8,
    if_true="publish",
    if_false="review",
)
def writer(state):
    return {"draft": "ready"}
```

## Retries and fallbacks

Instead of writing retry control flow outside the node, keep retry behavior near
the node:

```python
@app.node(next="writer", retry=2, on_fail="fallback_research")
def research(state):
    return {"notes": call_model(state.get("query"))}


@app.node(next="writer")
def fallback_research(state):
    return {"notes": "fallback notes"}
```

## Migration checklist

- Each node returns a non-empty dictionary.
- Each `next` target matches another node name or `"end"`.
- Conditional routes use real node names for `if_true` and `if_false`.
- Middleware does not swallow errors unless intended.
- Tests cover the graph path and at least one node in isolation.
