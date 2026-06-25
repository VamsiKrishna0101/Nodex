import json
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from nodex import Agent
from nodex.exceptions import NodexAuthError

load_dotenv()

app = Agent(name="research-pipeline", debug=True)
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


def _extract_text(response) -> str:
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [part.get("text", "") if isinstance(part, dict) else str(part) for part in content]
        return "".join(parts)
    return str(content)


@app.middleware
def logger(state, next_node):
    node = state._current_node
    print(f"\n[nodex] entering {node}")
    result = next_node(state)
    print(f"[nodex] completed {node}")
    return result


@app.middleware
def auth_check(state, next_node):
    if not state.get("api_key"):
        raise NodexAuthError("Missing api_key in state")
    return next_node(state)


@app.node(next="analyst", retry=2, on_fail="fallback_researcher")
def researcher(state):
    query = state.get("query")
    response = llm.invoke(
        f"""Return JSON with keys summary, key_facts, confidence.
Topic: {query}
Return only JSON."""
    )
    tokens = response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0
    text = _extract_text(response)

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        data = {"summary": text, "key_facts": [], "confidence": 0.5}

    return {
        "research_data": data,
        "confidence": data.get("confidence", 0.5),
        "_tokens": tokens,
    }


@app.node(next="critic", retry=1)
def analyst(state):
    research = state.get("research_data")
    response = llm.invoke(
        f"""Analyze this research and return JSON with keys strengths,
weaknesses, recommendation, score.
Research: {json.dumps(research)}
Return only JSON."""
    )
    tokens = response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0
    text = _extract_text(response)

    try:
        analysis = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "recommendation": "revise",
            "score": 5,
        }

    return {
        "analysis": analysis,
        "recommendation": analysis.get("recommendation", "revise"),
        "quality_score": analysis.get("score", 5),
        "_tokens": tokens,
    }


@app.node(next="end", retry=1)
def critic(state):
    research = state.get("research_data")
    analysis = state.get("analysis")
    recommendation = state.get("recommendation")
    score = state.get("quality_score", 5)

    if recommendation == "reject":
        return {
            "final_report": None,
            "status": "rejected",
            "reason": "Research quality too low to publish",
        }

    response = llm.invoke(
        f"""Write a concise final report.
Research: {json.dumps(research)}
Analysis: {json.dumps(analysis)}
Quality score: {score}/10"""
    )
    tokens = response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0
    text = _extract_text(response)

    return {
        "final_report": text,
        "status": "published",
        "word_count": len(text.split()),
        "_tokens": tokens,
    }


@app.node(next="analyst")
def fallback_researcher(state):
    query = state.get("query")
    response = llm.invoke(f"Give me 3 key facts about: {query}")
    tokens = response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0
    text = _extract_text(response)

    return {
        "research_data": {
            "summary": text,
            "key_facts": [text],
            "confidence": 0.4,
        },
        "confidence": 0.4,
        "_tokens": tokens,
    }


if __name__ == "__main__":
    trace = app.run(
        {
            "query": "Impact of agentic AI systems on software engineering jobs",
            "api_key": os.getenv("GOOGLE_API_KEY"),
        }
    )

    print("\n" + "=" * 60)
    print("PIPELINE RESULTS")
    print("=" * 60)

    final_output = trace.results[-1].output if trace.results else {}
    status = final_output.get("status", "unknown")
    print(f"Status      : {status.upper()}")
    print(f"Total Cost  : ${trace.total_cost:.4f}")
    print(f"Total Tokens: {trace.total_tokens}")
    print(f"Duration    : {trace.total_duration}s")
    print(f"Nodes Run   : {len(trace.results)}")

    if status == "published":
        print(f"Word Count  : {final_output.get('word_count')}")
        print("\n" + "-" * 60)
        print("FINAL REPORT")
        print("-" * 60)
        print(final_output.get("final_report"))
    elif status == "rejected":
        print(f"\nRejected: {final_output.get('reason')}")
