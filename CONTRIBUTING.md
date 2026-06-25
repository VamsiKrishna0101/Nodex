# Contributing

Thanks for helping improve Nodex.

## Local setup

```bash
git clone https://github.com/VamsiKrishna0101/Nodex
cd Nodex
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

On macOS or Linux:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development workflow

1. Open or pick a GitHub issue.
2. Create a branch from `main`, for example `fix/middleware-state-continuity`.
3. Make the smallest safe change.
4. Add or update tests for behavior changes.
5. Run checks locally.
6. Open a pull request linked to the issue.
7. Wait for CI to pass before merging.

Do not push code changes directly to `main`. Releases should happen only after the fix is merged and the maintainer approves a version tag.

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
- linked issue,
- tests added or updated,
- and any behavior users should know about.