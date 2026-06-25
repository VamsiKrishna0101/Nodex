# Contributing

Thanks for helping improve Nodex.

## Local setup

```bash
git clone https://github.com/VamsiKrishna0101/nodex
cd nodex
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

On macOS or Linux:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

Run these before opening a pull request:

```bash
ruff check src tests
pytest
```

## Development guidelines

- Keep the public API small and obvious.
- Prefer examples that run without extra infrastructure.
- Do not document behavior that is not covered by tests.
- Keep terminal output ASCII-safe so Windows users do not hit encoding issues.
- Add tests for user-facing behavior, especially CLI and graph execution paths.

## Pull requests

Include:

- what changed,
- why it changed,
- tests added or updated,
- and any behavior users should know about.
