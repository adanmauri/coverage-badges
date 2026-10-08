# 0005. Quality gates: pre-commit locally, MegaLinter in CI

**Status:** Accepted · **Date:** 2026-10-08

## Context

CI linted with MegaLinter (Python flavor) and nothing ran locally, although the README promised
pre-commit hooks. Problems surfaced only after a push, and an agent had no single command that
told it a change was done. The owner's other repositories run one `.pre-commit-config.yaml` from
the commit hook, `make check` and CI alike.

Running only pre-commit in CI would drop the non-Python linters the MegaLinter flavor ships (for
Markdown, YAML and JSON, among others). Running only MegaLinter keeps the slow feedback loop.
During the migration a pyright error reached a commit because the local hooks had no type checkers
while MegaLinter runs them, which shows the cost of the two lists drifting.

## Options

- **MegaLinter only:** one list, feedback only in CI, a heavy container to run it locally.
- **pre-commit everywhere, MegaLinter removed:** one list and fast feedback, but loses the
  non-Python linters unless each is added as a hook.
- **pre-commit locally, MegaLinter in CI:** fast local feedback on the checks that matter for the
  code, and the broad sweep stays in CI; the Python linters must appear in both.

## Decision

- **Locally:** [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) is the list. The commit
  hook runs it on staged files; `make lint` runs it on the whole repository; `make check` adds the
  tests on Python 3.14 and 3.10. It covers file hygiene, gitleaks, the `uv-lock` check, Black,
  isort, Ruff, Flake8, mypy, Pyright, Pylint and Bandit (through `uv run`), shellcheck, actionlint,
  zizmor on `action.yml`, agent pointer sync, docs links and the ADR index, and the commit-msg
  check against tool attribution.
- **In CI:** MegaLinter's Python flavor, configured in [`.mega-linter.yml`](../../.mega-linter.yml),
  plus the jobs in `.github/workflows/`: tests and the action itself (`tests.yaml`), Trivy and
  Bandit (`security.yaml`).
- Every Python linter MegaLinter runs is also a local hook, so a commit that passes locally does
  not fail there on Python code.

[`docs/DEVELOPMENT.md`](../DEVELOPMENT.md) keeps the map of which tool runs where.

## Consequences

### Positive

- `make check` is the definition of done for code, for people and agents alike.
- The commit hook catches most problems before a push.

### Negative / trade-offs

- Two lists to keep aligned: a Python linter added to one goes into the other.
- Tool versions differ between the two: the hooks pin the versions in `uv.lock` or their own
  `rev`, while MegaLinter brings its own.
- zizmor covers `action.yml` only until the existing workflow findings are fixed.

### Follow-ups

- `TODO.md`: fix the zizmor findings in the workflows and extend the hook to them; replace the
  deleted `aquasecurity/trivy-action@0.28.0` tag, which makes the Trivy job fail before it starts.
