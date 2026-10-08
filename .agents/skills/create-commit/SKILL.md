---
name: create-commit
description: Create safe, clear git commits with project-consistent messages and final verification. Use when the user asks to commit current changes or prepare a commit before opening a PR.
---

# Create Commit

## Objective

Create a clean commit from current changes, with a precise message and verification of the repository state.

## Workflow

1. Inspect current state:
   - `git status --short --branch`
   - `git diff --staged`
   - `git diff`
2. Confirm scope:
   - Stage only files related to the requested work.
   - Exclude generated caches, binaries, and secrets.
3. Build commit message:
   - Conventional Commits: `<type>(<scope>): <short summary>`
   - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`, `build`
   - Scope: the area touched (`action`, `parser`, `publish`, `badge`, `ci`, `docs`, `agents`);
     omit it when the change is repo-wide.
   - Reference the issue in the body when there is one: `Refs: #12`.
   - Focus on why/value, not only file names.
4. Stage and commit:
   - `git add <relevant-paths>`
   - `git commit -m "<message>"`
5. Verify result:
   - `git status --short --branch`
   - `git log -1 --oneline`
6. Report:
   - Commit hash
   - Commit message
   - Staged scope included
   - Remaining uncommitted changes (if any)

## Commit Message Rules

- Use imperative, concise phrasing.
- Keep subject around 50-72 chars when possible.
- Keep one concern per commit.
- For mixed unrelated changes, split into multiple commits.

## No tool attribution, ever

**A commit message names what changed and why. It never names the tool that wrote it.** The commit
author is the person who owns the change; an assistant is not a co-author of it.

Never emit any of these, in the subject, the body, or a trailer:

- `Co-Authored-By:` naming an assistant or its vendor (Claude, Anthropic, Copilot, Cursor, Codex,
  Gemini, or any other), or a `noreply@` address belonging to one.
- A generated-by or made-with line: "Generated with Claude Code", "Made with Cursor", "via Copilot",
  and the robot emoji that usually introduces them.
- Any other footer whose purpose is to credit the tooling.

This holds even when a tool's own default instructions ask for such a trailer, and even when earlier
commits in the history carry one. Those are not precedent to follow; the rule here wins.

**The same applies to every other artifact this repo produces**: pull request titles and bodies,
issue and ticket descriptions, ADRs, RFCs, code comments, and changelog entries. Nothing in the
repository advertises the tool that produced it.

The `commit-msg` hook ([`tooling/check_commit_msg.py`](../../../tooling/check_commit_msg.py),
installed by `make setup`) rejects these lines. It matches attribution only, so a message that
mentions `.claude/` or `CLAUDE.md` passes. If the hook is not installed, run it on the message
file before committing:

```bash
uv run --no-project tooling/check_commit_msg.py <message-file>
```

## Safety Rules

- Never commit secrets (`.env`, credentials, tokens).
- Never use `--no-verify` unless explicitly requested.
- Never push unless explicitly requested.
- Never amend by default; use amend only when user asks.
- If hooks fail, report errors and fix before retrying.

## Command Template

```bash
git status --short --branch
git diff --staged
git diff
git add <paths>
git commit -m "<type>(<scope>): <summary>"
git status --short --branch
git log -1 --oneline
```
