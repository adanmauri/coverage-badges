# 0007. Linter versions follow the MegaLinter image

**Status:** Accepted · **Date:** 2026-10-08

## Context

The same Python linters run twice ([ADR-0005](0005-quality-gates-pre-commit-locally-megalinter-in-ci.md)):
in the local hooks, at the versions in `uv.lock` or a hook `rev`, and in CI, at the versions
bundled in the MegaLinter image. Nothing tied the two together. The image pinned in CI (v9.1.0,
October 2025) shipped pylint 3.3.9, isort 6.1.0 and black 25.9.0 against 4.0.3, 7.0.0 and 25.11.0
in the lock; only flake8 and mypy matched. The latest image (v10.1.0) was ahead of the lock
instead. The two sides move on their own schedules (MegaLinter releases, Dependabot updates), so
aligning them once does not keep them aligned. A file could pass locally and fail in CI, or the
reverse.

Versions were not the only gap. When the repository has no config file by the name a MegaLinter
linter looks for, MegaLinter uses its own default: a `.pylintrc`, a `.mypy.ini` with
`ignore_missing_imports`, a `.ruff.toml` with line length 88. The local hooks read
`pyproject.toml`.

## Options

- **Let each side keep its versions:** no work, and the drift described above.
- **Run pre-commit in CI for the shared linters, MegaLinter only for the rest:** one version
  source, but two linting systems in CI.
- **Pin the local versions to the image's and check it:** MegaLinter stays the only CI linter,
  and every bump moves both sides in one change.

## Decision

The local versions are the image's, and a check fails when they differ.

- The `lint` group in `pyproject.toml` pins each linter with `==` to the version in the image
  that `code-quality.yaml` pins by commit. The local Python hooks run from `uv.lock`
  (`uv run --locked`), not from hook mirrors with their own `rev`.
- MegaLinter installs every linter in its own venv, so it ships isort 9.0.1 next to a pylint
  4.0.7 that requires `isort<9`. One environment cannot hold both, so isort has its own
  dependency group, declared in conflict with `lint` and resolved apart; its hook runs it with
  `uv run --isolated --group isort`.
- actionlint, shellcheck and zizmor are not Python packages here: their hook `rev` is the image's
  version.
- [`tooling/check_linter_versions.py`](../../tooling/check_linter_versions.py) reads the image's
  Dockerfile at the pinned commit and compares all of them. It runs in CI before MegaLinter, and
  as a hook when a file that holds a version changes.
- Dependabot ignores the pinned linters in the `uv` ecosystem and updates the MegaLinter action
  in the `github-actions` one. That pull request fails the check until the pins are updated to the
  new image's versions in the same pull request.
- [`.mega-linter.yml`](../../.mega-linter.yml) points the Python linters at `pyproject.toml`, so CI
  reads the settings the hooks read.

## Consequences

### Positive

- A commit that passes the hooks passes the same linters in CI, at the same versions and with the
  same settings.
- Bumping a linter is one pull request that moves both sides.

### Negative / trade-offs

- A linter release reaches this repository only when MegaLinter ships it.
- The check needs network access to read the Dockerfile.
- The image's other linters (Markdown, YAML, spelling, secrets, dependency scanners) run only in
  CI. Locally, gitleaks runs where the image has betterleaks.

### Follow-ups

- [`docs/DEVELOPMENT.md`](../DEVELOPMENT.md) describes how to bump MegaLinter.
