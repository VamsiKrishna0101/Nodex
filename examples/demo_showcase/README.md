# Demo Showcase

A deterministic demo script for videos and live presentations.

It demonstrates:

- `@app.node` graph steps
- `next="..."` flow control
- middleware audit logging
- retry behavior
- fallback node behavior
- conditional routing with `@app.route`
- state access with `state.get(...)`
- execution trace output
- token and cost tracking through `_tokens`

Run:

```bash
python examples/demo_showcase/agent.py
```

No LLM API key is required.