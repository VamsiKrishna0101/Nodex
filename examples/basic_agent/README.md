# Basic Agent

This example shows the smallest useful Nodex flow:

1. Research a topic.
2. Pass the result through state.
3. Write a final summary.

## Setup

```bash
pip install nodex langchain-google-genai python-dotenv
```

Set your Gemini API key:

```bash
set GOOGLE_API_KEY=your_key_here
```

On macOS or Linux:

```bash
export GOOGLE_API_KEY=your_key_here
```

## Run

```bash
python examples/basic_agent/agent.py
```

## What to look for

The terminal trace should show two nodes:

```text
OK  research
OK  writer
OK  Completed
```

The final printed output is the summary returned by the `writer` node.
