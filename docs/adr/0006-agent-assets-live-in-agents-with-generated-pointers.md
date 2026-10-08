# 0006. Agent assets live in `.agents/` with generated pointers

**Status:** Accepted · **Date:** 2026-10-07

## Context

Agent guidance was a single `.cursorrules` file, which only Cursor reads. Claude Code, Cursor and
GitHub Copilot each read instructions from their own location, so supporting all three by hand
means three copies that drift. The owner's other repositories (boxytrack, qi-ingestion) keep one
copy and generate the rest, and this repository works like them.

## Options

- **One file per tool, written by hand:** simple, but three copies of every rule.
- **Symlinks from each tool's location:** one copy, but not portable (Windows, some tools ignore
  them).
- **One canonical copy in `.agents/`, with thin generated pointers per tool:** one copy, portable,
  and drift is detectable by a script.

## Decision

- [`AGENTS.md`](../../AGENTS.md) at the root is the canonical manual ([agents.md](https://agents.md/)
  standard). `CLAUDE.md` and `.github/copilot-instructions.md` are hand-written pointers to it.
- Rules (`.agents/rules/`) and skills (`.agents/skills/`) live once, following the
  [`.agents` protocol](https://dotagentsprotocol.com/), with `SKILL.md` spelled for Claude Code.
- `tooling/sync_agents.py` (standard library) writes a pointer per tool: `.claude/skills/`,
  `.github/skills/`, `.github/instructions/`, `.cursor/rules/`. Pointers carry frontmatter and a
  link, never instructions, and are committed so a fresh clone works without a build step.
  `make check-agents`, also a pre-commit hook, fails on drift.
- The skills are the lightweight subset of the other repositories: `create-commit`, `write-pr`
  and `make-pr`, without tickets or a Definition of Done.
- No tool is credited in commits, PRs or docs; a commit-msg hook (`tooling/check_commit_msg.py`)
  rejects attribution lines.

## Consequences

### Positive

- One place to edit a rule or a skill, and every tool sees the change after `make sync-agents`.
- The same layout as the owner's other repositories, so moving between them costs nothing.

### Negative / trade-offs

- Generated files in four directories, which must not be edited by hand.
- When a tool reads `.agents/` natively, its pointers become dead weight to remove.

### Follow-ups

- [`.agents/README.md`](../../.agents/README.md) holds the operating procedure and cites this ADR.
