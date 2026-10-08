# 0009. Actions are pinned to a commit

**Status:** Accepted · **Date:** 2026-10-08

## Context

### How a workflow names the code it runs

A step such as `uses: actions/checkout@v5.1.0` names a git ref of another repository, and the
runner downloads whatever that ref points to when the job starts. Three kinds of ref are possible:

- **A major tag** (`@v5`) moves on purpose: its owner points it at every new `v5.x` release. A
  workflow that uses it runs different code after each release, with no change in this repository.
- **A version tag** (`@v5.1.0`) is meant to stay put, but it is a label like any other: its owner,
  or anyone holding the owner's credentials, can force-push it to another commit. The workflow
  keeps reading `@v5.1.0` and runs the new code.
- **A commit SHA** (`@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09`) is the hash of the code itself.
  It cannot point anywhere else: different code has a different SHA.

GitHub's immutable releases close the gap for a version tag, because the tag of an immutable
release cannot be moved or deleted. It is the publisher's choice, release by release: `v5.1.0` of
`actions/checkout` is not immutable (checked on 2026-10-08), while every `trivy-action` release
since `0.35.0` is.

### It happened to this repository

`security.yaml` runs Trivy and Bandit daily and on every push. It ran Trivy through
`aquasecurity/trivy-action@0.28.0`. From 2026-03-19 17:43 to 2026-03-20 05:40 UTC, an attacker had
force-pushed 76 of the 77 version tags of `aquasecurity/trivy-action`, including `0.28.0`, to code
that reads the runner's memory for secrets and sends them out
([GHSA-69fq-xp46-6x23](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23),
CVE-2026-33634).

This repository's scheduled run started at 2026-03-20 03:50 UTC, inside that window, and
succeeded. Nobody had changed anything here. Its logs have expired, so the commit the tag resolved
to cannot be confirmed; it has to be assumed the payload ran. What it could reach, checked on
2026-10-08:

- The repository has no Actions, environment or Dependabot secrets.
- The job's `GITHUB_TOKEN` had `contents: read` and `security-events: write` on a public
  repository, and expired when the job ended.
- No Actions cache is left, and the account has no `tpcp-docs-*` repository (the payload's
  fallback, which also needed a personal access token).

Nothing needed rotating. Aqua then deleted the rewritten tags and published new `v`-prefixed ones
as immutable releases. From 2026-03-21 the Trivy job failed before it started, every day, because
its tag no longer existed.

## Options

- **Major tags (`@v5`):** no upkeep, and every upstream release, or rewrite, runs here unseen.
- **Version tags (`@v5.1.0`):** readable, and safe only where the publisher made the release
  immutable, which has to be checked action by action and can change with the next release.
- **Version tags, but only for publishers considered trustworthy:** a judgement call per action;
  `trivy-action` came from a well-known security vendor.
- **Commit SHAs for every action, with the version in a comment:** a rewritten tag changes nothing
  here, whoever the publisher is. The SHA is unreadable, so the comment carries the version.

## Decision

- Every action in the workflows is pinned to a full commit SHA, with the version it corresponds to
  in a comment: `uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0`. No
  exception for first-party actions: deciding which publishers to trust is the judgement that
  failed with `trivy-action`.
- A container image runs by digest. The MegaLinter action, even pinned to a commit, pulled its
  image by tag (`ghcr.io/oxsecurity/megalinter-python:v10.1.0`), so `code-quality.yaml` runs the
  image directly, as `docker://...:v10.1.0@sha256:...` (added after the v1.0.0 release).
- zizmor enforces it, as a local hook and in MegaLinter.
- Dependabot updates actions monthly, with a 14-day cooldown, as for packages. It moves the SHA
  and the comment together, so an upgrade is a reviewed pull request, never a silent change.
- A tool an action downloads is pinned as well when the action allows it: `security.yaml` sets the
  Trivy binary to `v0.70.0`, because the same attack also published a malicious Trivy release.
- `security.yaml` stays, with `trivy-action` pinned to `v0.36.0` (an immutable release from April
  2026 that installs Trivy through a `setup-trivy` pinned by commit). It keeps its role: a daily
  scan, Trivy results in the repository's Security tab, and the Bandit report in the job summary.
- Checkouts drop their credentials (`persist-credentials: false`), except in the job that pushes
  the badge.

## Consequences

### Positive

- A rewritten or deleted tag cannot change the code a workflow runs.
- Every change to the code CI runs goes through a pull request in this repository.

### Negative / trade-offs

- A SHA says nothing to a reader; the version comment must stay next to it, and Dependabot keeps
  both in step.
- A fix released upstream reaches this repository only through that monthly pull request, two
  weeks after its release at the earliest.
- Trivy and Bandit run twice: in `security.yaml`, daily and reporting without blocking, and in
  MegaLinter, on pull requests and `main`, blocking.
- Dependabot does not update `docker://` references, so MegaLinter is bumped by hand.

### Follow-ups

- The workflow rules in [`coding-standards.md`](../../.agents/rules/coding-standards.md) cite
  this ADR.
