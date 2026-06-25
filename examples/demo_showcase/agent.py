"""Demo showcase for Nodex.

Run:
    python examples/demo_showcase/agent.py

This file is intentionally deterministic and does not need an LLM API key.
It demonstrates nodes, middleware, routing, retries, fallback, trace, tokens,
and state flow in one short script for a demo video.
"""

import os

from nodex import Agent

app = Agent(name="nodex-feature-showcase", debug=True)

attempts = {"risk_check": 0}
DEMO_RISK_SCORE = float(os.getenv("NODEX_DEMO_RISK_SCORE", "0.35"))


@app.middleware
def audit_log(state, next_node):
    print(f"[audit] entering={state._current_node} trace={state._trace}")
    result = next_node(state)
    print(f"[audit] next={state._current_node} trace={state._trace}")
    return result


@app.middleware
def require_topic(state, next_node):
    if not state.get("topic"):
        raise ValueError("Missing required topic")
    return next_node(state)


@app.node(next="research", retry=0)
def planner(state):
    topic = state.get("topic")
    return {
        "plan": [
            f"Research the core idea behind {topic}",
            "Score the risk",
            "Route to publish or review",
        ],
        "_tokens": 42,
    }


@app.node(next="risk_check")
def research(state):
    plan = state.get("plan", [])
    return {
        "notes": {
            "summary": "Nodex reduces LangGraph boilerplate with decorators.",
            "plan_steps": len(plan),
        },
        "risk_score": DEMO_RISK_SCORE,
        "_tokens": 88,
    }


@app.node(next="draft", retry=0, on_fail="fallback_risk_check")
def risk_check(state):
    attempts["risk_check"] += 1
    if attempts["risk_check"] == 1:
        raise RuntimeError("simulated transient model failure")

    return {
        "risk_status": "low" if state.get("risk_score", 1) < 0.5 else "high",
        "_tokens": 25,
    }


@app.node(next="draft")
def fallback_risk_check(state):
    return {
        "risk_status": "fallback-low",
        "fallback_used": True,
        "_tokens": 12,
    }


@app.node()
@app.route(
    condition=lambda state: state.get("risk_status") in {"low", "fallback-low"},
    if_true="publish",
    if_false="human_review",
)
def draft(state):
    notes = state.get("notes", {})
    return {
        "draft": f"Demo: {notes.get('summary')} Risk is {state.get('risk_status')}.",
        "_tokens": 64,
    }


@app.node(next="publish", human_review=True)
def human_review(state):
    return {"reviewed": True, "_tokens": 5}


@app.node(next="end")
def publish(state):
    return {
        "status": "published",
        "message": state.get("draft"),
        "trace_seen_by_user": list(state._trace),
        "_tokens": 18,
    }


if __name__ == "__main__":
    trace = app.run({"topic": "Nodex middleware and routing"})
    final = trace.results[-1].output

    print("\nFINAL DEMO OUTPUT")
    print(f"status : {final.get('status')}")
    print(f"message: {final.get('message')}")
    print(f"tokens : {trace.total_tokens}")
    print(f"cost   : ${trace.total_cost:.4f}")