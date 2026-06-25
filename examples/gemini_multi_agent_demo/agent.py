"""Real Gemini multi-agent demo for Nodex.

Run:
    pip install nodex-ai langchain-google-genai python-dotenv
    $env:GOOGLE_API_KEY="your_key_here"
    python examples/gemini_multi_agent_demo/agent.py

This demo intentionally uses 10 Gemini-backed nodes and a small per-node delay so
it feels like a real multi-agent pipeline in a demo video. You can adjust pacing:
    $env:NODEX_DEMO_NODE_DELAY="5"
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from nodex import Agent

load_dotenv()

MODEL_NAME = os.getenv("NODEX_DEMO_MODEL", "gemini-3.1-flash-lite")
NODE_DELAY_SECONDS = float(os.getenv("NODEX_DEMO_NODE_DELAY", "5"))
NODE_TIMEOUT_SECONDS = float(os.getenv("NODEX_DEMO_NODE_TIMEOUT", "120"))

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "Missing GOOGLE_API_KEY. In PowerShell run: "
        '$env:GOOGLE_API_KEY="your_key_here"'
    )

app = Agent(name="gemini-10-agent-launch-room", debug=True)
llm = ChatGoogleGenerativeAI(model=MODEL_NAME)


def _sleep_for_demo() -> None:
    if NODE_DELAY_SECONDS > 0:
        time.sleep(NODE_DELAY_SECONDS)


def _extract_text(response: Any) -> str:
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            else:
                parts.append(str(part))
        return "".join(parts)
    return str(content)


def _json_from_response(response: Any, fallback_key: str) -> dict:
    text = _extract_text(response).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {fallback_key: text}


def _tokens(response: Any) -> int:
    return response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0


def _ask_json(role: str, prompt: str, fallback_key: str) -> tuple[dict, int]:
    print(f"\n[gemini] {role} thinking with {MODEL_NAME}...")
    response = llm.invoke(prompt)
    _sleep_for_demo()
    return _json_from_response(response, fallback_key), _tokens(response)


@app.middleware
def audit_room(state, next_node):
    print(f"[audit] entering={state._current_node} trace={state._trace}")
    result = next_node(state)
    print(f"[audit] next={state._current_node} trace={state._trace}")
    return result


@app.node(next="market_researcher", timeout=NODE_TIMEOUT_SECONDS)
def mission_planner(state):
    data, tokens = _ask_json(
        "Mission Planner",
        f"""You are the mission planner for a startup launch room.
Return strict JSON with keys: objective, audience, success_metrics, work_plan.
Product idea: {state.get("idea")}
Return JSON only.""",
        "plan",
    )
    return {"plan": data, "_tokens": tokens}


@app.node(next="competitor_mapper", timeout=NODE_TIMEOUT_SECONDS)
def market_researcher(state):
    data, tokens = _ask_json(
        "Market Researcher",
        f"""You are a market researcher.
Return strict JSON with keys: market_pain, user_segments, buying_triggers.
Plan: {json.dumps(state.get("plan", {}))}
Return JSON only.""",
        "market_research",
    )
    return {"market_research": data, "_tokens": tokens}


@app.node(next="technical_architect", timeout=NODE_TIMEOUT_SECONDS)
def competitor_mapper(state):
    data, tokens = _ask_json(
        "Competitor Mapper",
        f"""You are a competitor analyst.
Return strict JSON with keys: alternatives, differentiation, positioning_gap.
Product idea: {state.get("idea")}
Market research: {json.dumps(state.get("market_research", {}))}
Return JSON only.""",
        "competitors",
    )
    return {"competitors": data, "_tokens": tokens}


@app.node(next="risk_analyst", timeout=NODE_TIMEOUT_SECONDS)
def technical_architect(state):
    data, tokens = _ask_json(
        "Technical Architect",
        f"""You are a technical architect.
Return strict JSON with keys: architecture, integrations, implementation_risks.
Product idea: {state.get("idea")}
Plan: {json.dumps(state.get("plan", {}))}
Return JSON only.""",
        "technical_plan",
    )
    return {"technical_plan": data, "_tokens": tokens}


@app.node(next="pricing_strategist", timeout=NODE_TIMEOUT_SECONDS)
def risk_analyst(state):
    data, tokens = _ask_json(
        "Risk Analyst",
        f"""You are a skeptical risk analyst.
Return strict JSON with keys: risk_score, top_risks, mitigations.
Risk score must be a number from 0 to 1.
Technical plan: {json.dumps(state.get("technical_plan", {}))}
Competitors: {json.dumps(state.get("competitors", {}))}
Return JSON only.""",
        "risk_report",
    )
    risk_score = data.get("risk_score", 0.5)
    try:
        risk_score = float(risk_score)
    except (TypeError, ValueError):
        risk_score = 0.5
    return {"risk_report": data, "risk_score": risk_score, "_tokens": tokens}


@app.node(next="launch_writer", timeout=NODE_TIMEOUT_SECONDS)
def pricing_strategist(state):
    data, tokens = _ask_json(
        "Pricing Strategist",
        f"""You are a pricing strategist.
Return strict JSON with keys: pricing_model, free_tier, paid_tiers, rationale.
Audience: {json.dumps(state.get("plan", {}).get("audience", {}))}
Market: {json.dumps(state.get("market_research", {}))}
Return JSON only.""",
        "pricing",
    )
    return {"pricing": data, "_tokens": tokens}


@app.node(timeout=NODE_TIMEOUT_SECONDS)
@app.route(
    condition=lambda state: state.get("risk_score", 1) >= 0.65,
    if_true="safety_reviewer",
    if_false="launch_writer",
)
def launch_writer(state):
    data, tokens = _ask_json(
        "Launch Writer",
        f"""You are a launch copywriter.
Return strict JSON with keys: headline, subheadline, launch_post, cta.
Idea: {state.get("idea")}
Pricing: {json.dumps(state.get("pricing", {}))}
Differentiation: {json.dumps(state.get("competitors", {}))}
Return JSON only.""",
        "launch_copy",
    )
    return {"launch_copy": data, "_tokens": tokens}


@app.node(next="qa_reviewer", timeout=NODE_TIMEOUT_SECONDS)
def safety_reviewer(state):
    data, tokens = _ask_json(
        "Safety Reviewer",
        f"""You are a safety and claims reviewer.
Return strict JSON with keys: approved_claims, risky_claims, required_edits.
Launch copy: {json.dumps(state.get("launch_copy", {}))}
Risk report: {json.dumps(state.get("risk_report", {}))}
Return JSON only.""",
        "safety_review",
    )
    return {"safety_review": data, "_tokens": tokens}


@app.node(next="final_editor", timeout=NODE_TIMEOUT_SECONDS)
def qa_reviewer(state):
    data, tokens = _ask_json(
        "QA Reviewer",
        f"""You are a QA reviewer for the launch plan.
Return strict JSON with keys: quality_score, missing_details, approval_status.
Quality score must be 1 to 10.
Plan: {json.dumps(state.get("plan", {}))}
Launch copy: {json.dumps(state.get("launch_copy", {}))}
Risk: {json.dumps(state.get("risk_report", {}))}
Return JSON only.""",
        "qa_review",
    )
    return {"qa_review": data, "_tokens": tokens}


@app.node(next="end", timeout=NODE_TIMEOUT_SECONDS)
def final_editor(state):
    data, tokens = _ask_json(
        "Final Editor",
        f"""You are the final editor.
Return strict JSON with keys: final_summary, demo_script, launch_checklist, verdict.
Combine everything into a concise founder-ready launch brief.
Plan: {json.dumps(state.get("plan", {}))}
Market: {json.dumps(state.get("market_research", {}))}
Competitors: {json.dumps(state.get("competitors", {}))}
Technical: {json.dumps(state.get("technical_plan", {}))}
Pricing: {json.dumps(state.get("pricing", {}))}
Launch copy: {json.dumps(state.get("launch_copy", {}))}
QA: {json.dumps(state.get("qa_review", {}))}
Return JSON only.""",
        "final_brief",
    )
    return {"final_brief": data, "_tokens": tokens}


if __name__ == "__main__":
    started = time.perf_counter()
    trace = app.run(
        {
            "idea": "Nodex, an Express.js-style Python framework for building LangGraph agents with decorators, middleware, routing, retries, and tracing."
        },
        raise_errors=False,
    )
    elapsed = time.perf_counter() - started
    if not trace.success:
        print("\nDEMO STOPPED: fix the provider/model error above and run again.")
        raise SystemExit(1)

    final = trace.results[-1].output.get("final_brief", {}) if trace.results else {}

    print("\n" + "=" * 72)
    print("FINAL MULTI-AGENT BRIEF")
    print("=" * 72)
    print(json.dumps(final, indent=2))
    print("\n" + "=" * 72)
    print("RUN STATS")
    print("=" * 72)
    print(f"Nodes run   : {len(trace.results)}")
    print(f"Tokens      : {trace.total_tokens}")
    print(f"Est. cost   : ${trace.total_cost:.4f}")
    print(f"Wall time   : {elapsed:.1f}s")
    print(f"Model       : {MODEL_NAME}")
    print(f"Node timeout: {NODE_TIMEOUT_SECONDS}s")