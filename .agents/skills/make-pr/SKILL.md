---
name: make-pr
description: Create pull requests with consistent title/body, correct base branch, and verified branch state. Use when the user asks to open a PR from the current branch.
---

# Make Pull Request

## Objective

Open a pull request from the current branch: validate state, push, and create
the PR. The body content is produced by the `write-pr` skill: this skill owns
the **mechanics**, not the prose.

## Workflow

1. Validate repository state:
   - `git status --short --branch`
   - Confirm current branch is not `main`.
2. Understand PR scope:
   - `git log --oneline origin/main...HEAD`
   - `git diff --stat origin/main...HEAD`
3. Ensure remote branch exists:
   - If needed: `git push -u origin HEAD`
4. Draft PR title:
   - Format: `<type>(<scope>): <short outcome>`, e.g. `feat(parser): read Clover reports`
   - Reuse commit intent when possible.
5. Get the PR body from the **`write-pr`** skill (it fills the repo template into
   `pr-body.tmp`). If `write-pr` has not been run, run it first, do not draft
   the body here.
6. Create PR:
   - Let `gh` apply the repo template automatically:
     `gh pr create --base main --head <branch> --title "<title>"` (opens the
     template to fill), or pass the filled template via `--body-file <file>`.
   - Or a GitHub MCP server if one is connected.
7. Report outcome:
   - PR URL
   - base/head branches
   - final title used

## Safety Rules

- Never open PR from `main`.
- Never force push unless explicitly requested.
- Do not change git config.
- If `gh` (or a GitHub MCP) is not authenticated, stop and ask the user to authenticate.

## Body

The PR body comes from the `write-pr` skill, which fills the repo template
([`.github/PULL_REQUEST_TEMPLATE.md`](../../../.github/PULL_REQUEST_TEMPLATE.md))
into `pr-body.tmp`. `gh pr create` also applies that template automatically when
no body is passed.

## Command Template

```bash
git status --short --branch
git log --oneline origin/main...HEAD
git diff --stat origin/main...HEAD
git push -u origin HEAD
# Applies .github/PULL_REQUEST_TEMPLATE.md automatically:
gh pr create --base main --head <branch> --title "<title>"
# Or, with a pre-filled body file based on that template:
gh pr create --base main --head <branch> --title "<title>" --body-file pr-body.tmp
```
