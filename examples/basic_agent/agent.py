from langchain_google_genai import ChatGoogleGenerativeAI

from nodex import Agent

app = Agent(name="research-agent", debug=True)
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


@app.node(next="writer")
def research(state):
    query = state.get("query")
    response = llm.invoke(f"Research this topic in 3 bullet points: {query}")

    tokens = response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0

    return {
        "research_results": response.content,
        "_tokens": tokens
    }


@app.node(next="end")
def writer(state):
    results = state.get("research_results")
    response = llm.invoke(f"Write a short summary based on: {results}")

    tokens = response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0

    return {
        "final_output": response.content,
        "_tokens": tokens
    }


if __name__ == "__main__":
    trace = app.run({"query": "Latest AI agent frameworks in 2026"})
    print("\n--- Final Output ---")
    output = trace.results[-1].output
    if isinstance(output.get("final_output"), list):
        print(output["final_output"][0]["text"])
    else:
        print(output.get("final_output"))
