---
description: Coding standards for AI agents and humans working in Coverage Badges
---

# Rules: coding standards

Binding checklist. The tools enforce most of it: `make check` locally, MegaLinter in CI.

## Python

- MUST run on **Python 3.10+** with the standard library only in `src/` (see the
  [action guardrails](action-guardrails.md)). Development uses Python 3.14 with Pipenv.
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

## Dependencies

- Pipenv: runtime packages pinned (`==`), dev packages `*`. The action itself has no runtime
  dependencies, and adding one needs approval.
