# Human In The Loop

This example demonstrates `human_review=True`.

When a node uses human review, Nodex prints the node output and asks for
terminal approval before the graph continues.

## Run

```bash
python examples/human_in_the_loop/agent.py
```

Approve the node output:

```text
Approve and continue? [y/n]: y
```

Reject the node output:

```text
Approve and continue? [y/n]: n
```

If rejected, Nodex raises a `NodexNodeError`.
