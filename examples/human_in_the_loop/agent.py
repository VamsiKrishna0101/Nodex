from nodex import Agent

app = Agent(name="human-review-demo", debug=True)


@app.node(next="review", retry=0)
def draft(state):
    topic = state.get("topic", "Nodex")
    return {"draft": f"Short launch note about {topic}"}


@app.node(next="publish", human_review=True)
def review(state):
    return {"approved_draft": state.get("draft")}


@app.node(next="end")
def publish(state):
    return {"status": "published", "content": state.get("approved_draft")}


if __name__ == "__main__":
    app.run({"topic": "decorator-first LangGraph agents"})
