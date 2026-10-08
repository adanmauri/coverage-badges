# 0007. Non-Python linter versions follow the MegaLinter image

**Status:** Accepted · **Date:** 2026-10-08

## Context

Most linters run twice ([ADR-0005](0005-quality-gates-pre-commit-locally-megalinter-in-ci.md)):
in the local hooks and in CI, inside the MegaLinter image. Nothing tied the two together. The image
pinned in CI (v9.1.0, October 2025) shipped pylint 3.3.9, isort 6.1.0 and black 25.9.0 against
4.0.3, 7.0.0 and 25.11.0 in the lock, so a file could pass locally and fail in CI, or the reverse.
The Markdown, YAML, JSON, spelling and secret linters ran only in CI, so their findings appeared
only after a push.

Versions were not the only gap. When the repository has no config file by the name a MegaLinter
linter looks for, MegaLinter uses its own default: a `.pylintrc`, a `.mypy.ini` with
`ignore_missing_imports`, a `.ruff.toml` with line length 88, a `.markdownlint.json` with line
length 400. The local tools used theirs.

## Options

- **Let each side keep its versions and settings:** no work, and the drift above.
- **Pin every local linter to the image's version:** the same results everywhere, but the Python
  development dependencies become `==` pins that move only with MegaLinter, Dependabot has to
  ignore them, and isort needs a group of its own (the image ships isort 9 next to a pylint that
  required `isort<9`). Tried first; the owner prefers unpinned development dependencies.
- **Pin to the image only what needs a pin anyway:** a pre-commit hook outside uv must name a
  version, so it names the image's. The Python linters stay ordinary development dependencies.

## Decision

The settings are shared everywhere; the versions are shared for the non-Python linters.

- [`.mega-linter.yml`](../../.mega-linter.yml) points the Python linters at `pyproject.toml`, and
  the settings MegaLinter would take from its defaults live in the repository
  (`.markdownlint.json`, `.yamllint.yml`, `.secretlintrc.json`, `.jscpd.json`), so both sides
  read the same files.
- The Python linters are development dependencies like any other: unpinned in `pyproject.toml`,
  locked in `uv.lock`, updated by Dependabot. Their hooks run them with `uv run --locked`. They
  can be ahead of or behind the image's.
- Every other linter in the image that checks files offline is a local hook at the image's
  version: markdownlint, markdown-table-formatter, prettier, jsonlint, cspell, secretlint and jscpd
  (Node.js, in `additional_dependencies`), shfmt (Go, the same), and betterleaks (which replaces
  gitleaks), actionlint, shellcheck and zizmor (their `rev`). pre-commit installs the Node.js and
  Go runtimes when they are missing. bash-exec and `git diff --check` are covered by the
  pre-commit-hooks checks for shebangs, whitespace and merge markers.
- Nothing checks the alignment automatically: a script that compared the hooks with the image's
  Dockerfile, in CI and as a hook, was tried and dropped at the owner's request. The pull request
  that bumps MegaLinter updates the hook versions by hand, from the image's Dockerfile.
- The scanners that need the network or a vulnerability database (Trivy, Grype, OSV-Scanner,
  trufflehog, checkov, lychee, v8r) run only in CI.

## Consequences

### Positive

- A Markdown, YAML, JSON, spelling, secret or shell finding shows up on commit, the same way CI
  reports it.
- The Python development dependencies update on their own schedule.

### Negative / trade-offs

- A Python linter can disagree between the hooks and CI while their versions differ (on
  2026-10-08, pylint 4.0.9 locally and 4.0.7 in the image).
- A MegaLinter bump that forgets the hooks lets them drift silently until a linter disagrees.
- The first `make setup` downloads Node.js and Go if missing, and builds shfmt and betterleaks.
- A scanner finding shows up only in CI.

### Follow-ups

- [`docs/CI.md`](../CI.md) describes how to bump MegaLinter.
