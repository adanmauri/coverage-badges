# Coverage Badges: agent operating guidelines

Canonical, vendor-neutral instructions for AI agents working in this repo
([agents.md](https://agents.md/) standard). `CLAUDE.md` and `.github/copilot-instructions.md` are
thin pointers here.

## What this repo is

A composite GitHub Action (`action.yml`) that reads a coverage report, generates an SVG badge and
publishes it so it renders in **private** repository READMEs. The value of the project rests on
one verified fact, kept in the README's [Why](README.md#why) table: `raw.githubusercontent.com`
images do not render in private READMEs, `github.com/OWNER/REPO/raw/BRANCH/...` renders on the
desktop web only, and only a relative path on the README's own branch renders in the mobile app.
Do not change a badge URL form without re-verifying it (see [Verification](#verification)).

## Read before working

| Concern | Source |
| ------- | ------ |
| What the action does, inputs, outputs, supported reports | [`README.md`](README.md) |
| Setup, commands, which check runs where, conventions | [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) |
| Decisions and their rationale | [`docs/adr/`](docs/adr/README.md) |
| Hard constraints on the action code | [`.agents/rules/action-guardrails.md`](.agents/rules/action-guardrails.md) |
| Code style and tooling | [`.agents/rules/coding-standards.md`](.agents/rules/coding-standards.md) |
| Pending work | [`TODO.md`](TODO.md) |
| How agent assets are organized | [`.agents/README.md`](.agents/README.md) |
| Lessons from past sessions | [`docs/RETRO-LOG.md`](docs/RETRO-LOG.md) |

## Layout

```text
action.yml                  composite action: computes, then publishes from the default branch only
scripts/publish-badge.sh    pushes the badge with git plumbing, never touching the caller's checkout
src/coverage_report.py      report parsers and format detection
src/badge_generator.py      SVG generation
src/generate_badge.py       CLI the action calls; prints the value shown in the badge
tests/fixtures/             one sample report per format, all describing 6 of 8 lines covered (75%)
tooling/                    repo scripts (agent pointer sync, commit-msg hook), not shipped
```

## Workflow

0. **Once per clone:** `make setup` installs the git hooks (pre-commit and commit-msg). Needs `uv`.
1. **Branch** from an up-to-date `main`: `feat/...`, `fix/...`, `docs/...`, `chore/...`.
2. **Commit** with the `create-commit` skill (Conventional Commits, no tool attribution).
3. **Open the PR** with `write-pr` (body) and `make-pr` (mechanics).
4. **Record decisions:** a change that reverses or extends an ADR comes with a new one, from
   [`docs/adr/template.md`](docs/adr/template.md); rules cite the ADR instead of repeating it.
5. **Close the loop:** run `retro` after a substantive session.

## Before you finish

- `make check` passes: every hook in [`.pre-commit-config.yaml`](.pre-commit-config.yaml) over the
  whole repo, then the tests on Python 3.14 and on 3.10 (the oldest Python the action supports).
- A change to parsing adds a fixture or a case in `tests/test_coverage_report.py`; a change to
  publishing adds a case in `tests/test_publish_badge.py`.
- README, `action.yml` descriptions and this file agree with the change.
- CI also runs MegaLinter (`.github/workflows/code-quality.yaml`), which `make check` does not.

## Verification

Unit tests cover parsing, SVG generation and the publish script against a local bare repository.
They cannot prove a badge **renders**. When a change touches publishing or badge URLs:

1. Push the action into a throwaway **private** repository, run it there on a real runner
   (`gh workflow run`, `gh run watch`), and check the target branch with `gh api`.
2. Ask the user to look at the README logged in, on the desktop web and in the mobile app. An
   agent cannot see a private README rendered; do not report rendering as verified without them.
3. Creating and deleting that repository is outward-facing: ask first. Deleting needs the
   `delete_repo` scope (`gh auth refresh -h github.com -s delete_repo`).

## Boundaries

- Never push to `main`, force-push, or rewrite shared history unless the user asks for it.
- Never create tags or releases, or publish to the Marketplace, without explicit approval:
  users pin `@v1`, so a tag is a public contract.
- Never add a runtime dependency to the action. It runs on the runner's `python3` with the
  standard library only (see the guardrails).
- Never bypass the hooks (`--no-verify`) or weaken a check to make it pass.
- Never attribute work to an AI tool in commits, PRs, docs or comments (see `create-commit`).
- Edit agent assets only under `.agents/`, then run `make sync-agents`; never edit the generated
  pointers in `.claude/skills/`, `.github/skills/`, `.github/instructions/` or `.cursor/rules/`.

## Skills

| Skill | Use it to |
| ----- | --------- |
| `create-commit` | Commit a scoped change with a Conventional Commit message |
| `write-pr` | Fill the PR template into `pr-body.tmp` |
| `make-pr` | Push and open the PR against `main` |
| `retro` | Capture lessons and improve this workspace |
