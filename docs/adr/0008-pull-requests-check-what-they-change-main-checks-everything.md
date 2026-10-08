# 0008. Pull requests check what they change; main checks everything

**Status:** Accepted · **Date:** 2026-10-08

## Context

Every pull request linted the whole repository and ran every workflow, whatever it touched. A
finding in a file the pull request did not change is noise for its author, and a pull request that
only edits docs gains nothing from the tests. The owner asked for pull requests to check what
changed, and for a merge to `main` to check everything.

## Options

- **Everything on every pull request:** simplest, and the noise above.
- **Only what changed, everywhere:** fastest, but nothing ever looks at the whole repository, so
  findings that span files are never seen.
- **What changed on pull requests, everything on `main` and on a schedule:** focused pull
  requests, and full runs where nobody is waiting.

## Decision

What changed on pull requests; everything on push to `main` and on the weekly scheduled run.

- **MegaLinter** gets `VALIDATE_ALL_CODEBASE: false` on pull requests and lints the files that
  differ from the merge base with `main` (`git diff origin/main...`). The checkout fetches the full
  history, because without the merge base MegaLinter falls back to a diff that also lists what
  landed on `main` since the branch started.
- A pull request that changes a file that decides what the linters report (`.mega-linter.yml`,
  `.pre-commit-config.yaml`, `pyproject.toml`, `.flake8`, `.cspell.json`, `code-quality.yaml`)
  lints everything. Otherwise a stricter rule would pass its own pull request, which lints only the
  config file, and fail `main`.
- MegaLinter's project-mode linters (Trivy, Grype, OSV-Scanner, Syft, Semgrep, betterleaks,
  secretlint, trufflehog, checkov, jscpd, ls-lint) always scan the whole repository; MegaLinter
  cannot narrow them. They are fast, and their findings are not tied to a file.
- **Tests** run in full whenever they run: selecting tests by diff would miss a change that breaks
  a module through another one. Pull requests that touch none of the action's or the tests' files
  skip the workflow; `main` always runs it, and publishes the badge.
- **Locally**, the hooks run on the staged files, and mypy, Pyright, Pylint and Bandit check the
  whole project whenever a Python file changes (`pass_filenames: false`).

## Consequences

### Positive

- A pull request shows findings in the files it touches, and docs-only pull requests do not wait
  for the tests.

### Negative / trade-offs

- A pull request can pass and `main` fail, on a check that spans files (duplicated code, a module
  importing one that changed) or on a file the pull request did not touch. The fix goes in the next
  pull request.
- `main` has no branch protection today. If a check ever becomes required, the `paths` filter on
  the tests leaves it pending on docs-only pull requests and blocks the merge; the filter would
  then move into a job that skips itself.

### Follow-ups

- The scope logic lives in [`code-quality.yaml`](../../.github/workflows/code-quality.yaml) and
  [`tests.yaml`](../../.github/workflows/tests.yaml).
