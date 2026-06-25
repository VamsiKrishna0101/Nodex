# Multi-Node Pipeline

This example demonstrates a larger Nodex graph with:

- middleware,
- auth checks,
- retry and fallback behavior,
- JSON parsing,
- multiple LLM-powered nodes,
- and a final report.

## Flow

```text
researcher -> analyst -> critic -> end
      |
      +-> fallback_researcher -> analyst
```

## Setup

```bash
pip install nodex langchain-google-genai python-dotenv
```

Set `GOOGLE_API_KEY` before running:

```bash
set GOOGLE_API_KEY=your_key_here
```

## Run

```bash
python examples/multi_node_pipeline/agent.py
```

## Notes

The example asks Gemini to return JSON. If the model returns plain text, the
example falls back to a conservative default structure so the pipeline can keep
moving.
