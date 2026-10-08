# 0009. Actions are pinned to a commit

**Status:** Accepted · **Date:** 2026-10-08

## Context

`security.yaml` runs Trivy and Bandit daily and on every push. It ran Trivy through
`aquasecurity/trivy-action@0.28.0`. From 2026-03-19 17:43 to 2026-03-20 05:40 UTC, an attacker had
force-pushed 76 of the 77 version tags of `aquasecurity/trivy-action`, including `0.28.0`, to code
that reads the runner's memory for secrets and sends them out
([GHSA-69fq-xp46-6x23](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23),
CVE-2026-33634).

This repository's scheduled run started at 2026-03-20 03:50 UTC, inside that window, and
succeeded. Its logs have expired, so the commit the tag resolved to cannot be confirmed; it has to
be assumed the payload ran. What it could reach, checked on 2026-10-08:

- The repository has no Actions, environment or Dependabot secrets.
- The job's `GITHUB_TOKEN` had `contents: read` and `security-events: write` on a public
  repository, and expired when the job ended.
- No Actions cache is left, and the account has no `tpcp-docs-*` repository (the payload's
  fallback, which also needed a personal access token).

Nothing needed rotating. Aqua then deleted the rewritten tags and published new `v`-prefixed ones
as immutable releases. From 2026-03-21 the Trivy job failed before it started, every day, because
its tag no longer existed.

A tag is a label its owner, or anyone holding the owner's credentials, can move to other code;
every workflow that references it then runs the new code with no change on this side. A commit
SHA names the content itself.

## Options

- **Reference actions by tag:** readable, and open to the rewrite above.
- **Pin every action to a commit SHA, with the version in a comment:** a rewritten tag changes
  nothing here; Dependabot updates the SHA and the comment together.

## Decision

- Every action in the workflows is pinned to a full commit SHA, with the version in a comment.
  zizmor enforces it, as a local hook and in MegaLinter.
- `security.yaml` stays, with `trivy-action` pinned to `v0.36.0` (an immutable release from April
  2026 that installs Trivy v0.70.0 through a `setup-trivy` pinned by commit). It keeps its role:
  a daily scan, Trivy results in the repository's Security tab, and the Bandit report in the job
  summary.
- Dependabot updates actions monthly, with a 14-day cooldown, as for packages.
- Checkouts drop their credentials (`persist-credentials: false`), except in the job that pushes
  the badge.

## Consequences

### Positive

- A rewritten tag cannot change the code a workflow runs.

### Negative / trade-offs

- Trivy and Bandit run twice: in `security.yaml`, daily and reporting without blocking, and in
  MegaLinter, on pull requests and `main`, blocking.
- The MegaLinter action runs its image by tag (`ghcr.io/oxsecurity/megalinter-python:v10.1.0`),
  which pinning the action to a commit does not freeze.

### Follow-ups

- `TODO.md`: run the MegaLinter image by digest.
