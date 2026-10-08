# Architecture

How the action works inside, for people changing it. How to use it is in the
[README](../README.md).

## Flow

[`action.yml`](../action.yml) is a composite action with a single `bash` step:

1. **Choose the target** from `mode`: in `branch` mode, the `branch` input (default `badges`) and
   the URL `https://github.com/OWNER/REPO/raw/BRANCH/PATH`; in `commit` mode, the default branch
   and `PATH` as a relative URL.
2. **Compute the value and draw the badge:** `python3 -m src.generate_badge` reads the report,
   writes the SVG to `$RUNNER_TEMP` and prints the value it shows.
3. **Set the outputs** `coverage` and `markdown`.
4. **Publish, only from the default branch:** on any other ref it stops with a notice, so pull
   requests compute the value without publishing. On the default branch it calls
   `scripts/publish-badge.sh` and sets `published` to `true` when it pushed a new badge.
5. **Write the job summary** with the value and the Markdown snippet for the README.

| File                       | Role                                                                |
|----------------------------|---------------------------------------------------------------------|
| `src/coverage_report.py`   | One parser per report format, and format detection                  |
| `src/badge_generator.py`   | The SVG: label, value and color                                     |
| `src/generate_badge.py`    | The CLI the action calls; prints the value shown in the badge       |
| `scripts/publish-badge.sh` | Pushes the badge to a branch without touching the caller's checkout |

## Runtime

The action runs inside other people's jobs, so it installs nothing there. It uses `bash`, `git`
and the runner's own `python3`, never `pip`, `uv` or `actions/setup-python`, and the code in
`src/` and `scripts/` uses the Python standard library only.

- **Python 3.10 is the floor.** GitHub-hosted Ubuntu runners ship 3.10 or newer (3.10.12 on Ubuntu
  22.04). Newer syntax is a `SyntaxError` there, so the tests also run on 3.10, locally
  (`make test-compat`) and in CI on the system Python of Ubuntu 22.04.
- **macOS** runners ship a newer `python3` but have not been tested. **Windows** is not supported.
- **XML reports** are parsed with `xml.etree`. Bandit flags it; the input is the caller's own CI
  artifact, so the findings carry a `# nosec` instead of adding a `defusedxml` dependency.

## The value

Every format contributes **line coverage**, the one metric all of them report:

| Format                | Number used                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------|
| Cobertura             | `line-rate` of the root element                                                                |
| JaCoCo                | the report-level `LINE` counter                                                                |
| LCOV                  | `LH`/`LF` per file, or its `DA` lines when a file has no totals                                |
| Go coverprofile       | statements; a block listed twice (with `-coverpkg`) counts once, covered if any copy was       |
| coverage.py JSON      | its own total, which includes branches when branch coverage is on, as `coverage report` prints |
| Istanbul json-summary | `total.lines`                                                                                  |

A report with no coverable lines is an error, never 0% or 100%.

The value is **truncated** to one decimal, never rounded: 99.96% shows as 99.9%, so the badge never
claims more coverage than there is, and a value never crosses a color threshold upward (green from
80%, yellow-green from 60%, yellow from 40%, red below). A tolerance of 1e-6 absorbs float noise,
so 28.999999999 shows as 29.0%. The badge can therefore show 0.1% less than a tool's own summary,
which rounds.

## Where the badge is published

A private repository's README shows images only from URLs the viewer's session can read. Tested
on 2026-10-07 in a throwaway private repository:

| URL form                                                              | Desktop web | GitHub mobile app (Android) |
|-----------------------------------------------------------------------|:-----------:|:---------------------------:|
| `raw.githubusercontent.com/OWNER/REPO/BRANCH/...`                     |     no      |             no              |
| `github.com/OWNER/REPO/raw/BRANCH/...` and `blob/BRANCH/...?raw=true` |     yes     |             no              |
| Relative `../../raw/BRANCH/...` from a root README                    |     yes     |             no              |
| Relative path on the README's own branch                              |     yes     |             yes             |

The browser loads `github.com/.../raw/...` with the viewer's session; `raw.githubusercontent.com`
gets no session and fails. Coverage services and shields.io endpoints need the data on a public
URL, so they do not work either. The action offers the two forms that do:

- **`branch` (default):** an orphan `badges` branch, linked as `github.com/OWNER/REPO/raw/...`.
  It keeps badge commits out of the default branch and works when that branch is protected, which
  private repositories usually do. It does not render in the mobile app.
- **`commit`:** the default branch, linked by relative path. It renders everywhere, but adds bot
  commits to the default branch and fails when that branch is protected.

The action never outputs a `raw.githubusercontent.com` or shields.io URL. How GitHub renders these
URLs is undocumented and can change, so a new URL form, or a doubt about an existing one, is
checked again in a throwaway private repository by a person looking at the README (`AGENTS.md`,
Verification). The iOS app has not been tested.

## Publishing

`scripts/publish-badge.sh <badge-file> <branch> <path> <message>` builds the commit with git
plumbing on a temporary index (`GIT_INDEX_FILE`), so the caller's checkout and working tree are
never touched:

1. Store the SVG as a blob (`git hash-object -w`).
2. If the branch exists on `origin`, fetch it and load its tree (`git read-tree`); if it does not
   (`git ls-remote` exits with 2), start an orphan branch.
3. Put the blob at the path (`git update-index --cacheinfo`) and write the tree. If the tree did
   not change, print `unchanged` and stop: an identical badge never makes a commit.
4. Commit as `github-actions[bot]` (`git commit-tree`), with a message ending in `[skip ci]`, so a
   badge commit on the default branch does not start the workflow again.
5. Push. When a concurrent run pushed first, retry from step 2, up to three times. Print `pushed`.

It pushes with the credentials `actions/checkout` leaves in the repository, so the job needs
`permissions: contents: write`, and fails with a hint when the push is rejected (missing
permission, or a ruleset that blocks `github-actions[bot]`).
