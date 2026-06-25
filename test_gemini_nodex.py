"""Temporary real Gemini smoke test for nodex-ai.

Before running:
    pip install langchain-google-genai
    $env:GOOGLE_API_KEY="your_key_here"
    python test_gemini_nodex.py

Delete this file after testing if you want.
"""

import os

from langchain_google_genai import ChatGoogleGenerativeAI

from nodex import Agent


api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError(
        "GOOGLE_API_KEY is not set. In PowerShell run: "
        '$env:GOOGLE_API_KEY="your_key_here"'
    )

app = Agent(name="gemini-live-smoke-test", debug=True)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=api_key,
)


@app.node(next="writer", retry=1)
def research(state):
    topic = state.get("topic", "LangGraph developer experience")
    response = llm.invoke(
        f"Give exactly 3 short bullet points about this topic: {topic}"
    )
    return {
        "research_notes": response.content,
        "_tokens": (esponse.usage_metadata or {}).get("total_tokens", 0),
    }


@app.node(next="end", retry=1)
def writer(state):
    notes = state.get("research_notes")
    response = llm.invoke(
        "Turn these notes into one short launch sentence for developers:\n"
        f"{notes}"
    )
    return {
        "final_output": response.content,
        "_tokens": (response.usage_metadata or {}).get("total_tokens", 0),
    }


if __name__ == "__main__":
    trace = app.run({"topic": "Nodex for LangGraph agents"})
    final = trace.results[-1].output.get("final_output")
    print("\n--- Gemini Final Output ---")
    print(final)