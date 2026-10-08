# 0009. Actions are pinned to a commit, and security scans run in MegaLinter

**Status:** Accepted · **Date:** 2026-10-08

## Context

`security.yaml` ran Trivy through `aquasecurity/trivy-action@0.28.0` and Bandit, daily and on
every push. From 2026-03-19 17:43 to 2026-03-20 05:40 UTC, an attacker had force-pushed 76 of the
77 version tags of `aquasecurity/trivy-action`, including `0.28.0`, to code that reads the runner's
memory for secrets and sends them out
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

Nothing needed rotating. Aqua then deleted the rewritten tags, and from 2026-03-21 the job failed
before it started, every day, with nobody noticing. Both scans had `continue-on-error: true`, so
they never blocked anything. The MegaLinter Python flavor already ships Trivy and Bandit; Bandit
was disabled there to avoid running it twice.

## Options

- **Repin `trivy-action` to a safe commit:** fixes the job and keeps a third-party action that
  receives the token.
- **Drop `security.yaml` and use MegaLinter's scanners:** one action fewer; the scans block like
  every other linter.

## Decision

- `security.yaml` is gone. MegaLinter runs Trivy, Grype and OSV-Scanner on the repository and
  Bandit on `src/` (the code the action runs), and blocks on their findings. A weekly scheduled run
  of `code-quality.yaml` lints everything, so a new advisory against an unchanged dependency still
  surfaces.
- Every action in the workflows is pinned to a full commit SHA, with the version in a comment.
  zizmor enforces it, as a local hook and in MegaLinter.
- Dependabot updates actions monthly, with a 14-day cooldown, as for packages.
- Checkouts drop their credentials (`persist-credentials: false`), except in the job that pushes
  the badge.

## Consequences

### Positive

- A rewritten tag cannot change the code a workflow runs.
- One fewer third-party action with access to the token.

### Negative / trade-offs

- The MegaLinter action runs its image by tag (`ghcr.io/oxsecurity/megalinter-python:v10.1.0`),
  which pinning the action to a commit does not freeze.
- Trivy results no longer go to the repository's Security tab; they are in the MegaLinter report.
- A Bandit or Trivy finding now fails CI instead of passing unnoticed.

### Follow-ups

- `TODO.md`: run the MegaLinter image by digest.
