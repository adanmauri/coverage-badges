---
description: Hard constraints on the GitHub Action code (action.yml, scripts/, src/)
---

# Rules: action guardrails

The action runs inside other people's workflows, often in private repositories. These constraints
keep it safe to drop into any job. Each section cites the ADR that holds the rationale.

## Runtime: [ADR-0002](../../docs/adr/0002-the-action-runs-on-the-runner-python-with-the-standard-library.md)

- MUST run on the runner's own `python3`, **3.10 or newer**, with the **standard library only**.
  No `pip install`, no `uv`, no `actions/setup-python` inside the action: uv is the development
  toolchain, not a requirement for the people who use the action. Python 3.12+ syntax (for
  example, reusing the same quote type inside an f-string) is a `SyntaxError` on 3.10.
- MUST run on GitHub-hosted Ubuntu and macOS runners with `bash`, `git` and `python3`.

## Publishing: [ADR-0001](../../docs/adr/0001-publish-badges-where-private-readmes-render-them.md)

- MUST NOT modify the caller's checkout: no `git checkout`, `git add`, `git commit` or `git stash`
  in the workspace. `publish-badge.sh` builds commits with plumbing on a temporary index.
- MUST publish only from the default branch. Other refs compute the value and set outputs only.
- MUST NOT create a commit when the badge did not change.
- Commits are authored by `github-actions[bot]` and carry `[skip ci]`.
- Push with the credentials left by `actions/checkout`; never ask for or embed a personal token.

## Badge URLs: [ADR-0001](../../docs/adr/0001-publish-badges-where-private-readmes-render-them.md)

- The `markdown` output MUST use a form verified to render in private repositories: the
  `github.com/OWNER/REPO/raw/BRANCH/PATH` form in `branch` mode, a relative path in `commit` mode.
  NEVER `raw.githubusercontent.com` or a shields.io endpoint.
- A new URL form needs a rendering check by a person (see `AGENTS.md`, Verification).

## Inputs and values: [ADR-0003](../../docs/adr/0003-the-badge-never-overstates-coverage.md)

- Pass inputs to `run:` steps through `env:`, never by interpolating `${{ inputs.* }}` into the
  script (template injection).
- The value is truncated to one decimal, never rounded up: the badge must not overstate coverage.
