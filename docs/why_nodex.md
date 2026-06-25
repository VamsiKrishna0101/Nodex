# Why Nodex

Nodex exists because LangGraph is powerful but not always quick to start with.

For production-grade agents, LangGraph gives you a serious graph runtime. But
many teams still spend time on repetitive setup:

- defining state shape,
- registering nodes,
- wiring edges,
- adding retries,
- handling fallbacks,
- tracing execution,
- testing individual nodes,
- and remembering which graph edge failed.

Nodex keeps the LangGraph mental model and reduces the ceremony around it.

## The Express.js comparison

Express did not replace Node.js. It gave developers a clean way to express a
server:

```javascript
app.get("/", handler)
```

Nodex tries to do the same for LangGraph agents:

```python
@app.node(next="writer")
def research(state):
    return {"notes": "data"}
```

The goal is not magic. The goal is obvious code.

## What Nodex optimizes for

- Small first example.
- Clear node ownership.
- Middleware for cross-cutting behavior.
- Retry and fallback behavior near the node.
- Terminal traces that show what ran.
- Test helpers for node-level tests.

## What Nodex does not try to do

- It does not replace LangGraph.
- It does not choose an LLM provider for you.
- It does not hide your agent logic.
- It does not promise that every graph can be reduced to decorators.

## Best use cases

Nodex is a good fit when you want:

- a small or medium LangGraph agent,
- readable graph structure,
- built-in tracing,
- a CLI scaffold,
- and a clean path from prototype to tested code.

If you need advanced LangGraph features directly, you can still drop down to
LangGraph concepts. Nodex is a layer, not a lock-in.
