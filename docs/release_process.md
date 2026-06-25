# Release Process

Nodex releases use GitHub Actions and PyPI Trusted Publishing.

## Normal Fix Flow

1. Open a GitHub issue describing the bug or change.
2. Create a branch from `main`.
3. Commit the fix and tests on that branch.
4. Open a pull request linked to the issue.
5. Wait for CI to pass.
6. Merge the pull request.
7. Bump the version in `pyproject.toml` and `src/nodex/__init__.py` if the PR did not already do it.
8. Push a tag such as `v0.1.1` only after the maintainer approves the release.

## Patch Release Commands

```bash
git checkout main
git pull origin main
git tag v0.1.1
git push origin v0.1.1
```

The `Publish` workflow builds the package and publishes to PyPI.

## Important Rule

Do not push code fixes directly to `main` and do not tag releases before the fix has gone through issue and PR review.