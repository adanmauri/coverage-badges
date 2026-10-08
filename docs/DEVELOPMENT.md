# Development

How to set up, check and change this repository. What the action does for its users is in the
[README](../README.md); why things are the way they are is in the [ADRs](adr/README.md).

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

| Command                      | What it does                                                                                                                                 |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `make check`                 | `lint`, then `test` and `test-compat`: the definition of done for code                                                                       |
| `make lint`                  | Every hook in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) over the whole repository                                              |
| `make test`                  | `uv run pytest` with coverage, on the development Python                                                                                     |
| `make test-compat`           | The tests on Python 3.10 in a throwaway environment ([ADR-0002](adr/0002-the-action-runs-on-the-runner-python-with-the-standard-library.md)) |
| `make check-linter-versions` | Fail if a non-Python hook's version differs from the MegaLinter image (needs network)                                                        |
| `make sync-agents`           | Regenerate the agent pointers from `.agents/`                                                                                                |
| `make check-agents`          | Fail if the agent pointers drifted                                                                                                           |
| `make help`                  | List the targets                                                                                                                             |

The badge generator runs on its own as well:
`uv run python -m src.generate_badge --report coverage.xml -o coverage.svg`.

## Quality gates

Two lists, aligned on purpose ([ADR-0005](adr/0005-quality-gates-pre-commit-locally-megalinter-in-ci.md)):
the pre-commit hooks run on every commit and in `make lint`; MegaLinter and the tests run in CI.
A linter in both runs at the same version in both
([ADR-0007](adr/0007-non-python-linter-versions-follow-the-megalinter-image.md)). Pull requests check what
they change, `main` checks everything
([ADR-0008](adr/0008-pull-requests-check-what-they-change-main-checks-everything.md)).

| Tool                                   | Checks                                                                                  |       Local hook       | CI                                        |
|----------------------------------------|-----------------------------------------------------------------------------------------|:----------------------:|-------------------------------------------|
| pre-commit-hooks                       | whitespace, end of file, YAML, TOML, large files, merge markers, shebangs, private keys |          yes           |                                           |
| betterleaks, secretlint                | secrets in the repository                                                               |          yes           | MegaLinter                                |
| uv-lock                                | `uv.lock` matches `pyproject.toml`                                                      |          yes           | `uv sync --locked` fails                  |
| Black, isort                           | formatting, import order (Black profile, 100 columns)                                   |          yes           | MegaLinter                                |
| Ruff, Flake8, Pylint                   | lint                                                                                    |          yes           | MegaLinter                                |
| mypy, Pyright                          | types                                                                                   |          yes           | MegaLinter                                |
| Bandit                                 | security issues in `src/`                                                               |          yes           | MegaLinter, `security.yaml`               |
| shellcheck                             | `scripts/*.sh`                                                                          |          yes           | MegaLinter                                |
| actionlint                             | workflow syntax and expressions                                                         |          yes           | MegaLinter                                |
| zizmor                                 | security of `action.yml`, the workflows and `dependabot.yaml`                           |          yes           | MegaLinter                                |
| shfmt                                  | shell formatting                                                                        |          yes           | MegaLinter                                |
| markdownlint, markdown-table-formatter | Markdown style and table layout                                                         |          yes           | MegaLinter                                |
| yamllint, prettier, jsonlint           | YAML and JSON syntax and formatting                                                     |          yes           | MegaLinter                                |
| cspell                                 | spelling (project words in `.cspell.json`)                                              |          yes           | MegaLinter                                |
| jscpd                                  | copied code                                                                             |          yes           | MegaLinter                                |
| `tooling/check_linter_versions.py`     | the non-Python hooks above match the MegaLinter image's versions                        | when a version changes | `code-quality.yaml`                       |
| `tooling/sync_agents.py --check`       | agent pointers in sync with `.agents/`                                                  |          yes           |                                           |
| `tooling/check_docs.py`                | relative links in Markdown, ADR numbering and index                                     |          yes           |                                           |
| `tooling/check_commit_msg.py`          | no tool attribution in the commit message                                               |       commit-msg       |                                           |
| pytest                                 | tests on 3.14 with coverage, and on 3.10                                                |      `make check`      | `tests.yaml`                              |
| The action itself                      | publishes this repository's badge from `main`                                           |                        | `tests.yaml`                              |
| Trivy, Grype, OSV-Scanner, checkov     | vulnerable dependencies, misconfigured workflows                                        |                        | MegaLinter; Trivy also in `security.yaml` |
| trufflehog                             | verified secrets                                                                        |                        | MegaLinter                                |
| lychee, v8r                            | broken links, files that do not match their JSON schema                                 |                        | MegaLinter                                |

Every linter MegaLinter runs on files offline is also a local hook, with the same settings file
and, except for the Python linters, the same version. The scanners that need the network or a vulnerability database run only in
CI. Every active linter blocks. One that does not fit this repository is
disabled in [`.mega-linter.yml`](../.mega-linter.yml) with the reason, never left running without
blocking. Each setting is explained there.

### CI workflows

| Workflow             | Runs on                                                                                      | Jobs                                                                                                                                          |
|----------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `tests.yaml`         | push to `main`; PRs that touch the action, its scripts, `src/`, `tests/` or the Python setup | tests with coverage, then the action publishes the badge (`main` only); the generator on the system Python 3.10 of Ubuntu 22.04               |
| `code-quality.yaml`  | push and PR to `main`                                                                        | linter versions check, then MegaLinter (Python flavor): the changed files on PRs, everything on `main` and on PRs that change linter settings |
| `security.yaml`      | push and PR to `main`, daily                                                                 | Trivy (results in the Security tab) and Bandit (report in the job summary); neither blocks                                                    |
| `todo-to-issue.yaml` | push to `main`                                                                               | turns `TODO` and `FIXME` comments in code into issues                                                                                         |

Actions are pinned to a commit SHA with the version in a comment
([ADR-0009](adr/0009-actions-are-pinned-to-a-commit.md)).
Dependabot ([`.github/dependabot.yaml`](../.github/dependabot.yaml)) opens monthly updates for
`uv.lock` and the actions, for releases at least 14 days old.

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

- `tests/test_coverage_report.py`: one parser per format against `tests/fixtures/`. Every fixture
  describes the same project (6 of 8 lines covered), so a parser bug shows up as a number other
  than 75.0.
- `tests/test_generate_badge.py`: the CLI, including truncation
  ([ADR-0003](adr/0003-the-badge-never-overstates-coverage.md)) and error exits.
- `tests/test_publish_badge.py`: `scripts/publish-badge.sh` against a local bare repository,
  isolated from your git configuration.
- **Rendering cannot be unit tested.** A change to publishing or badge URLs is verified in a
  throwaway private repository, with a person looking at the README; see `AGENTS.md`,
  Verification, and [ADR-0001](adr/0001-publish-badges-where-private-readmes-render-them.md).

## Dependencies

uv for everything ([ADR-0004](adr/0004-uv-is-the-development-toolchain.md)); never `pip`.

- The action has no runtime dependencies (`dependencies = []`), and adding one needs approval.
- Development tools are in the `test` and `lint` groups, unpinned in `pyproject.toml` and pinned
  in `uv.lock`; Dependabot updates them. The Python linters can therefore differ from the
  MegaLinter image's ([ADR-0007](adr/0007-non-python-linter-versions-follow-the-megalinter-image.md)).
- The non-Python hooks pin the image's version: in `additional_dependencies` (Node.js and Go
  packages) or as their `rev` (betterleaks, actionlint, shellcheck, zizmor).
- **Bumping MegaLinter** (usually a Dependabot pull request): `make check-linter-versions` lists
  every hook whose version changed. Update those in `.pre-commit-config.yaml`, run `make check`,
  fix what the new versions report, and push it all in the same pull request.
- Adding a non-Python linter: add it as a hook at the image's version, and to
  `tooling/check_linter_versions.py`.

## Agent assets

AI agents follow [`AGENTS.md`](../AGENTS.md). Rules and skills live once in
[`.agents/`](../.agents/README.md) and reach each tool through generated pointers
([ADR-0006](adr/0006-agent-assets-live-in-agents-with-generated-pointers.md)).

## Releasing

Not done yet: users will pin `adanmauri/coverage-badges@v1`, so the first tag is a public contract.
The steps are tracked in [`TODO.md`](../TODO.md).
