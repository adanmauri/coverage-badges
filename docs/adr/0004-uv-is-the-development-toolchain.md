# 0004. uv is the development toolchain

**Status:** Accepted · **Date:** 2026-10-08

## Context

The project declared its tools in a Pipfile, while the maintainer works with uv, as in the
owner's other repositories, and the tests already ran through `uv run` to get a Python 3.10
interpreter for the compatibility check. Two toolchains for one small repository meant two ways to
get an environment.

## Options

- **Keep Pipenv:** no migration, but a tool the maintainer does not use, and no way to get another
  interpreter for the 3.10 check without a second tool.
- **pip and `requirements*.txt`:** universal, but no lock with hashes per platform and no
  interpreter management.
- **uv:** one tool for interpreters, environments, locking and running; already used for the tests
  and in the owner's other repositories.

## Decision

uv for everything in development:

- `pyproject.toml` declares the project with `dependencies = []` (see
  [ADR-0002](0002-the-action-runs-on-the-runner-python-with-the-standard-library.md)) and the
  `test` and `lint` dependency groups, unpinned; `dev` includes both and is uv's default group.
- `uv.lock` and `.python-version` (3.14) are committed.
- `make` targets, the local pre-commit hooks and CI (`astral-sh/setup-uv`, `uv sync --locked`)
  call uv. The 3.10 tests run in an isolated environment (`uv run --isolated --python 3.10`), so
  the project `.venv` stays on 3.14.
- Dependabot watches the `uv` ecosystem.

uv is a development tool only: the action does not use it.

## Consequences

### Positive

- One command sets everything up (`make setup`), and the same lock drives local runs and CI.
- The `uv-lock` hook rejects a `pyproject.toml` change without its lock.

### Negative / trade-offs

- Contributors need uv installed.
- MegaLinter does not use this environment: it brings its own linters, whose versions can differ
  ([ADR-0007](0007-non-python-linter-versions-follow-the-megalinter-image.md)), and its
  pre-commands install the `test` group from the lock where the type checkers need pytest.

### Follow-ups

- [`coding-standards.md`](../../.agents/rules/coding-standards.md) cites this ADR for dependencies.
