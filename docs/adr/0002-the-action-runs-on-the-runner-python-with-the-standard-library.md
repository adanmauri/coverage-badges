# 0002. The action runs on the runner's Python with the standard library

**Status:** Accepted · **Date:** 2026-10-07

## Context

The action runs inside other people's jobs. Whatever it installs or changes there is a cost and a
risk for them: time, network access, a different Python on the `PATH` for their later steps, and a
supply chain they did not choose. The work itself is small: parse one report file, write one SVG,
push one commit.

## Options

- **Docker container action:** isolated, but Linux only and slow to start (image pull or build).
- **JavaScript action:** fast and the most common type, but a rewrite of the generator and a Node
  build and bundle to maintain.
- **Composite action with `actions/setup-python` and pip packages:** familiar, but changes the
  caller's Python and installs third-party code in their job.
- **Composite action on the runner's own `python3`, standard library only:** nothing to install.
  GitHub-hosted Ubuntu runners ship Python 3.10 or newer (verified: system Python 3.10.12 on
  Ubuntu 22.04). macOS runners ship a newer `python3`, but were not tested.

## Decision

`action.yml` is a composite action that runs `bash`, `git` and the runner's `python3`. The code it
runs (`src/`, `scripts/`) uses the standard library only and supports **Python 3.10 or newer**. It
never runs `pip`, `uv` or `actions/setup-python`. The project declares `dependencies = []`.

## Consequences

### Positive

- No install step: the action adds seconds to a job and nothing to its environment.
- No third-party code runs in the caller's job, so there is no dependency to audit or update.

### Negative / trade-offs

- Python 3.10 is the floor: newer syntax is a `SyntaxError` there. A badge generator with Python
  3.12 f-string syntax failed on 3.9 and 3.10 before this was written down, so it is now checked:
  `make test-compat` locally, and a CI job on the system Python of Ubuntu 22.04.
- XML reports are parsed with `xml.etree`, which bandit flags (B405, B314). The input is the
  caller's own CI artifact, so the findings carry a `# nosec` instead of a `defusedxml` dependency.
- Windows runners are not supported.

### Follow-ups

- [`action-guardrails.md`](../../.agents/rules/action-guardrails.md) cites this ADR for the runtime.
