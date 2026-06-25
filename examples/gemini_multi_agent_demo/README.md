# Gemini Multi-Agent Demo

A real Gemini-backed Nodex demo for launch videos.

It uses 10 LLM-backed nodes:

- mission planner
- market researcher
- competitor mapper
- technical architect
- risk analyst
- pricing strategist
- launch writer
- optional safety reviewer through routing
- QA reviewer
- final editor

Run:

```powershell
pip install nodex-ai langchain-google-genai python-dotenv
$env:GOOGLE_API_KEY="your_key_here"
python examples/gemini_multi_agent_demo/agent.py
```

By default the demo sleeps 5 seconds after each Gemini call so the run feels like
a substantial multi-agent workflow on video. Change pacing with:

```powershell
$env:NODEX_DEMO_NODE_DELAY="2"
```

Use a different Gemini model with:

```powershell
$env:NODEX_DEMO_MODEL="gemini-2.0-flash"
```
The demo sets each Nodex node timeout to 120 seconds because real LLM calls can be slower than local examples. Change it with:

```powershell
$env:NODEX_DEMO_NODE_TIMEOUT="180"
```

If you use a wrong model name, Gemini may not return a clean provider error before the Nodex timeout. In that case, check `NODEX_DEMO_MODEL` first.