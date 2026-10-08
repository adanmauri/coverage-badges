# Development

How to set up, check and change this repository. What the action does for its users is in the
[README](../README.md), how it works inside in [ARCHITECTURE.md](ARCHITECTURE.md), and what checks
a change, locally and in CI, in [CI.md](CI.md).

## Setup

Needs [uv](https://docs.astral.sh/uv/) and `git`. uv installs the Python versions it needs, and
pre-commit installs the Node.js and Go runtimes some hooks need when they are missing (the first
`make setup` takes a few minutes for that).

```bash
make setup   # uv sync --locked, then installs the pre-commit and commit-msg hooks
make check   # everything that must pass before a change is done
```

`make setup` creates `.venv` with the Python in `.python-version` (3.14) and the `dev` dependency
group. Editors pick it up from `.venv/bin/python` (VS Code is preconfigured).

## Commands

| Command             | What it does                                                                                    |
|---------------------|-------------------------------------------------------------------------------------------------|
| `make check`        | `lint`, then `test` and `test-compat`: the definition of done for code                          |
| `make lint`         | Every hook in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) over the whole repository |
| `make test`         | `uv run pytest` with coverage, on the development Python                                        |
| `make test-compat`  | The tests on Python 3.10, the oldest the action supports, in a throwaway environment            |
| `make sync-agents`  | Regenerate the agent pointers from `.agents/`                                                   |
| `make check-agents` | Fail if the agent pointers drifted                                                              |
| `make help`         | List the targets                                                                                |

The badge generator runs on its own as well:
`uv run python -m src.generate_badge --report coverage.xml -o coverage.svg`.

## Conventions

The binding checklist is [`.agents/rules/coding-standards.md`](../.agents/rules/coding-standards.md),
for people and agents alike, and the constraints on the action code are in
[`.agents/rules/action-guardrails.md`](../.agents/rules/action-guardrails.md). The short version:

- **Language:** code, comments, docs, commit messages and user-facing text in English.
- **Python:** 3.10+ syntax and standard library only in `src/`; built-in generics and `X | None`;
  type hints everywhere; a docstring on every module, class and public function.
- **Shell:** `set -euo pipefail`, every expansion quoted.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat(parser): ...`, `fix(publish): ...`), one concern per commit, no tool attribution.
- **Branches:** `feat/...`, `fix/...`, `docs/...`, `chore/...` from an up-to-date `main`; never
  push to `main`.
- **Pull requests:** fill [the template](../.github/PULL_REQUEST_TEMPLATE.md); the test plan lists
  only what was actually run.

## Testing

- `tests/test_coverage_report.py`: one parser per format against `tests/fixtures/`. There is one
  sample report per format, and all of them describe the same project: 8 lines, 6 of them covered.
  Every parser must return 75.0 for its fixture, so any other number points at a parser bug.
- `tests/test_generate_badge.py`: the CLI, including truncation (the badge never shows more than
  the real value) and error exits.
- `tests/test_publish_badge.py`: `scripts/publish-badge.sh` against a local bare repository,
  isolated from your git configuration.
- **Rendering cannot be unit tested.** A change to publishing or badge URLs is verified in a
  throwaway private repository, with a person looking at the README; see `AGENTS.md`,
  Verification, and [where the badge is published](ARCHITECTURE.md#where-the-badge-is-published).

## Dependencies

uv manages the interpreters, the environment, the lock and every command; never `pip`. It is a
development tool only: the action does not use it.

- The action has no runtime dependencies (`dependencies = []`), and adding one needs approval.
- Development tools are in the `test` and `lint` groups of `pyproject.toml`, unpinned there and
  pinned in `uv.lock`, which is committed. Add one with `uv add --group <test|lint> <package>`.
  `make setup` installs both groups (`dev`); CI installs only the group a job needs, with
  `--locked`.
- `.python-version` (3.14) is the development Python; the 3.10 tests run in a throwaway
  environment, so `.venv` stays on 3.14.
- Dependabot opens monthly updates for `uv.lock` and the actions, for releases at least 14 days
  old. Pick the same age when bumping anything by hand.
- The pre-commit hooks outside uv pin the MegaLinter image's versions; how to bump them is in
  [CI.md](CI.md#same-settings-and-mostly-the-same-versions).

## Agent assets

AI agents follow [`AGENTS.md`](../AGENTS.md), the one canonical instructions file; `CLAUDE.md` and
`.github/copilot-instructions.md` only point to it. Rules (`.agents/rules/`) and skills
(`.agents/skills/`) live once, in [`.agents/`](../.agents/README.md), and
`tooling/sync_agents.py` writes a thin pointer for each tool in `.claude/skills/`,
`.github/skills/`, `.github/instructions/` and `.cursor/rules/`. Pointers are generated and
committed: edit the file in `.agents/`, then run `make sync-agents`; `make check` fails when they
drift. No tool is credited in commits, pull requests or docs, and a commit-msg hook rejects
attribution lines.

## Releasing

Not done yet: users will pin `adanmauri/coverage-badges@v1`, so the first tag is a public contract.
The steps are tracked in [`TODO.md`](../TODO.md).
