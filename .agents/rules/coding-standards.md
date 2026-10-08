---
description: Coding standards for AI agents and humans working in Coverage Badges
---

# Rules: coding standards

Binding checklist. The tools enforce most of it: `make check` locally, MegaLinter in CI
([ADR-0005](../../docs/adr/0005-quality-gates-pre-commit-locally-megalinter-in-ci.md)). The map of which
tool runs where is in [`docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md#quality-gates).

## Python

- MUST run on **Python 3.10+** with the standard library only in `src/` (see the
  [action guardrails](action-guardrails.md)). Development uses the Python in `.python-version`.
- Built-in generics and unions: `dict[str, int]`, `list[str] | None`. Import from `typing` only
  what has no built-in form (`Any`, `cast`).
- Black and isort (Black profile), line length 100; Ruff, Flake8, Pylint, mypy and Pyright clean.
- Type hints on every function and method signature.
- Docstrings on every module, class and public function: a one-line summary, then a blank line and
  detail only when it adds something.
- Absolute imports with the `src.` prefix.
- Specific exceptions: `ValueError` for invalid input, `FileNotFoundError` for missing files. The
  message says what is wrong and, when it helps, what to do instead.
- Standard `logging`, no emojis in logs or messages.
- All code, comments and user-facing text in English.

## Shell

- `set -euo pipefail`; shellcheck clean.
- Quote every expansion. Do not rely on word splitting: agents often run commands from zsh, which
  does not split unquoted variables.

## Tests

- pytest under `tests/`, files `test_*.py`, one class per unit under test.
- Every public function has a test, failure paths included.
- Sample reports go in `tests/fixtures/` and describe the same 75% project, so a parser bug shows
  up as a different number.
- Tests that run git isolate themselves from the developer's git configuration
  (`GIT_CONFIG_GLOBAL=/dev/null`), see `tests/test_publish_badge.py`.

## Dependencies: [ADR-0004](../../docs/adr/0004-uv-is-the-development-toolchain.md)

- **uv** for everything: `uv sync`, `uv run`, `uv add --group <test|lint> <package>`. NEVER call
  `pip` or create a virtualenv by hand. Test tools are unpinned in `pyproject.toml` and pinned in
  `uv.lock`, which is committed; CI installs with `--locked`.
- Linters are pinned to the MegaLinter image's versions and move only with it
  ([ADR-0007](../../docs/adr/0007-linter-versions-follow-the-megalinter-image.md)). NEVER bump one
  on its own; `make check-linter-versions` fails if you do.
- The action itself has no runtime dependencies (`dependencies = []`), and adding one needs
  approval.

## Workflows: [ADR-0009](../../docs/adr/0009-actions-are-pinned-to-a-commit-and-security-scans-run-in-megalinter.md)

- Every `uses:` is pinned to a full commit SHA with the version in a comment
  (`@<sha> # v5.1.0`). `persist-credentials: false` on every checkout whose job does not push.
- A tag, release or package that disappeared or moved is a signal, not housekeeping: read the
  upstream advisories and check this repository's runs before replacing it.
- What a tool's container ships (versions, venvs, uv) is read from its Dockerfile at the pinned
  commit, never assumed.
