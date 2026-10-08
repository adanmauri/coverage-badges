# 0001. Publish badges where private READMEs render them

**Status:** Accepted · **Date:** 2026-10-07

## Context

The project started as a set of pre-generated SVGs (0%, 5%, ..., 100%) linked from other READMEs.
That added little over a shields.io static badge, which takes any value in the URL and needs no
data access. The need that is not covered is a badge that **updates itself** and **renders in the
README of a private repository**, without sending coverage data to a third party.

Coverage services and shields.io endpoints read the data from a public URL, so they do not work
for private repositories. Most badge actions push the SVG to the repository and link it through
`raw.githubusercontent.com`; `py-cov-action/python-coverage-comment-action`, for one, describes
itself as only "supposedly compatible" with private repositories.

On 2026-10-07 a throwaway private repository tested every URL form, with the SVG on an orphan
branch and a different SVG on the README's branch, viewed by a logged-in user with access:

| URL form | Desktop web | GitHub mobile app (Android) |
| -------- | :---------: | :-------------------------: |
| `raw.githubusercontent.com/OWNER/REPO/BRANCH/...` | no | no |
| `github.com/OWNER/REPO/raw/BRANCH/...` and `blob/BRANCH/...?raw=true` | yes | no |
| Relative `../../raw/BRANCH/...` from a root README | yes | no |
| Relative path on the README's own branch | yes | yes |

Anonymous requests to every form returned 404, as expected for a private repository. The browser
loads `github.com/.../raw/...` with the viewer's session, while `raw.githubusercontent.com` gets no
session and fails.

## Options

- **`raw.githubusercontent.com` on any branch:** what most actions do. Does not render in private
  repositories at all.
- **shields.io endpoint or a gist:** needs the data public, or a personal token with `gist` scope.
- **GitHub Pages:** public unless the organization has Enterprise Cloud; needs a paid plan for
  private repositories.
- **Orphan branch, linked as `github.com/OWNER/REPO/raw/BRANCH/PATH`:** renders on the desktop web,
  works with a protected default branch, keeps badge commits out of the main history. Does not
  render in the mobile app.
- **Commit to the default branch, linked by a relative path:** renders everywhere, but adds bot
  commits to the default branch and fails when that branch is protected.

## Decision

The action offers both working forms as `mode`:

- `branch` (default): push the SVG to an orphan branch (`badges`) and output
  `github.com/OWNER/REPO/raw/BRANCH/PATH`.
- `commit`: commit the SVG to the default branch and output the relative path.

It never outputs a `raw.githubusercontent.com` or shields.io URL. It publishes only from the
default branch; other refs compute the value and set the outputs. Publishing never touches the
caller's checkout (git plumbing on a temporary index), skips unchanged badges, and marks commits
`[skip ci]`.

`branch` is the default because private repositories usually protect their default branch, where
`commit` would fail out of the box, and READMEs are read mostly on the desktop web.

## Consequences

### Positive

- The badge renders in private repositories without third parties or extra tokens: the job only
  needs `permissions: contents: write`.
- The default branch history stays free of badge commits in `branch` mode.

### Negative / trade-offs

- In `branch` mode the badge does not render in the GitHub mobile app. The README states it.
- Badges of private repositories are visible only to viewers with access, like everything else in
  them.
- The rendering behavior is GitHub's, undocumented, and can change. A new URL form, or a doubt
  about an existing one, needs the same check by a person (see `AGENTS.md`, Verification).

### Follow-ups

- [`action-guardrails.md`](../../.agents/rules/action-guardrails.md) cites this ADR for publishing
  and badge URLs.
- `TODO.md`: check the iOS app, which was not tested.
