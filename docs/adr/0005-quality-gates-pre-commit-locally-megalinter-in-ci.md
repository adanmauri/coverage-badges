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
  tests on Python 3.14 and 3.10. It covers file hygiene, secrets, the `uv-lock` check, the Python
  linters (through `uv run`), shell, workflows, Markdown, YAML, JSON, spelling and copied code
  ([ADR-0007](0007-non-python-linter-versions-follow-the-megalinter-image.md) lists them), agent pointer sync,
  docs links and the ADR index, and the commit-msg check against tool attribution.
- **In CI:** MegaLinter's Python flavor, configured in [`.mega-linter.yml`](../../.mega-linter.yml),
  plus the tests and the action itself (`tests.yaml`) and the daily security scan
  (`security.yaml`).
- Every linter MegaLinter runs on files offline is also a local hook, with the same settings
  ([ADR-0007](0007-non-python-linter-versions-follow-the-megalinter-image.md)), so a commit that
  passes locally does not fail there unless a Python linter's version differs.

[`docs/DEVELOPMENT.md`](../DEVELOPMENT.md) keeps the map of which tool runs where.

## Consequences

### Positive

- `make check` is the definition of done for code, for people and agents alike.
- The commit hook catches most problems before a push.

### Negative / trade-offs

- Two lists to keep aligned: a Python linter added to one goes into the other.

### Follow-ups

- [ADR-0007](0007-non-python-linter-versions-follow-the-megalinter-image.md) ties the versions of the two
  lists together; [ADR-0008](0008-pull-requests-check-what-they-change-main-checks-everything.md)
  sets what each pull request checks.
