# Architecture Decision Records

One file per decision: `NNNN-<kebab-slug>.md` whose first line is `# NNNN. <Title>`, numbered
sequentially and never renumbered. A superseded ADR stays in place with its status changed and a
link to its successor. Start from [`template.md`](template.md).

The ADR holds the rationale; the rules in [`.agents/rules/`](../../.agents/rules/) hold the
checklist and cite the ADR instead of repeating it. `make check` fails on a numbering gap, a
heading that disagrees with its file name, an ADR missing from this index, or a broken relative
link anywhere in the docs. A number taken by a branch that has not merged yet goes under
**Reserved** so it is not reported as a gap.

| ADR | Title | Status |
| --- | ----- | ------ |
| [0001](0001-publish-badges-where-private-readmes-render-them.md) | Publish badges where private READMEs render them | Accepted |
| [0002](0002-the-action-runs-on-the-runner-python-with-the-standard-library.md) | The action runs on the runner's Python with the standard library | Accepted |
| [0003](0003-the-badge-never-overstates-coverage.md) | The badge never overstates coverage | Accepted |
| [0004](0004-uv-is-the-development-toolchain.md) | uv is the development toolchain | Accepted |
| [0005](0005-quality-gates-pre-commit-locally-megalinter-in-ci.md) | Quality gates: pre-commit locally, MegaLinter in CI | Accepted |
| [0006](0006-agent-assets-live-in-agents-with-generated-pointers.md) | Agent assets live in `.agents/` with generated pointers | Accepted |
| [0007](0007-linter-versions-follow-the-megalinter-image.md) | Linter versions follow the MegaLinter image | Accepted |
| [0008](0008-pull-requests-check-what-they-change-main-checks-everything.md) | Pull requests check what they change; main checks everything | Accepted |
| [0009](0009-actions-are-pinned-to-a-commit-and-security-scans-run-in-megalinter.md) | Actions are pinned to a commit, and security scans run in MegaLinter | Accepted |

## Reserved

None.
