# Nodex Quickstart

This guide gets you from an empty folder to a running Nodex agent.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install nodex-ai
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install nodex-ai
```

## Create an agent

Create `agent.py`:

```python
from nodex import Agent

app = Agent(name="quickstart-agent")


@app.node(next="writer")
def research(state):
    query = state.get("query", "LangGraph")
    return {"notes": f"Research notes about {query}"}


@app.node(next="end")
def writer(state):
    return {"final": state.get("notes").upper()}


if __name__ == "__main__":
    app.run({"query": "agent frameworks"})
```

Run it:

```bash
python agent.py
```

Expected output:

```text
>  nodex running - quickstart-agent
--------------------------------------------------
OK  research       ->  0.002s  |  tokens: 0  |  $0.0000
OK  writer         ->  0.001s  |  tokens: 0  |  $0.0000
--------------------------------------------------
OK  Completed  |  0.023s  |  $0.0000  |  2 nodes  |  0 failed  |  tokens: 0
```

## Use the CLI

```bash
nodex new my-agent
cd my-agent
pip install -r requirements.txt
nodex dev agent:app
```

Pass initial state as JSON:

```bash
nodex run agent:app --input '{"query":"hello"}'
```

## What to remember

- Nodes receive `NodexState`.
- Nodes return a non-empty `dict`.
- `next="end"` finishes the graph.
- `retry=N` retries a failed node.
- `on_fail="some_node"` redirects to a fallback node after retries.
- Middleware wraps node execution.
