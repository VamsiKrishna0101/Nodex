# Agent Contribution Guide

This file is for AI coding agents working on Nodex.

## Rules

- Read the relevant source files before editing.
- Keep `src/nodex` behavior aligned with `README.md`, `docs/`, and `site/`.
- Use ASCII-safe terminal output unless there is a tested reason not to.
- Do not introduce provider-specific dependencies into the core package.
- Add or update tests for behavior changes.
- Run `ruff check src tests` and `pytest` before handing off.

## Important behavior

- `Agent.run()` returns an `ExecutionTrace`.
- Node functions must return a non-empty dictionary.
- `next="end"` finishes the graph.
- Middleware wraps node execution in registration order.
- Route metadata should work in both decorator orders.
- Testing helpers are public through `nodex.testing`.

## Do not

- Revert user work without explicit instruction.
- Replace LangGraph internals with a custom graph engine.
- Document features that do not exist.
- Add large framework dependencies to the docs site without asking.
