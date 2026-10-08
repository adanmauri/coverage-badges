---
name: write-pr
description: Compose a clear, review-ready pull request body from the diff/commits by filling the repo PR template. Use when the user wants to draft a PR description (the mechanics of opening it live in make-pr).
---

# Write Pull Request Body

## Objective

Produce a review-ready PR body from the current branch's changes, filling the
repo's PR template. This skill **writes content only**, opening the PR is the
`make-pr` skill's job.

## Workflow

1. Understand the scope of the change:
   - `git log --oneline origin/main...HEAD`
   - `git diff --stat origin/main...HEAD`
   - Read the actual diff for anything non-obvious.
2. Identify the related GitHub issue or `TODO.md` item, if any, from the conversation or the
   commits. Its expectations become the PR's verification list.
3. Fill the repo PR template, **do not invent a different structure**:
   [`.github/PULL_REQUEST_TEMPLATE.md`](../../../.github/PULL_REQUEST_TEMPLATE.md)
   - **Summary**: 2-4 bullets, impact on action users first (new input, changed output,
     changed badge URL).
   - **Verification**: what was actually run, with the result: `make check`, and for
     publishing or URL changes the private-repo run described in `AGENTS.md`. Never list a
     check that was not run.
   - **Notes**: breaking changes for users pinned to `@v1`, follow-ups, or omit.
4. Write the filled body to a gitignored scratch file `pr-body.tmp` (matched by
   `*.tmp`) so `make-pr` can pass it via `--body-file`.
5. Show the drafted body to the user.

## Rules

- Explain impact first; keep bullets concrete and reviewable.
- Avoid generic text like "misc fixes" or "various changes".
- Link the issue when there is one.
- Never paste secrets or tokens.
- Keep the template's section structure intact (single source of truth).
- **No tool attribution.** No "Generated with", no "Made with", no robot emoji, no footer crediting
  an assistant or its vendor, even when a tool's own defaults ask for one. The same rule the
  `create-commit` skill states for commit messages applies to every word of the PR.
