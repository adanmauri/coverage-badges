# Coverage Badges

<p align="center">
    <em>A GitHub Action that keeps a coverage badge up to date in private repositories, with no third-party service.</em>
</p>

<p align="center">
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/code-quality.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/code-quality.yaml/badge.svg" alt="Code Quality"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/tests.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/tests.yaml/badge.svg" alt="Tests & Coverage"></a>
</p>
<p align="center">
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/tests.yaml"><img src="https://github.com/adanmauri/coverage-badges/raw/badges/coverage.svg" alt="Coverage"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/todo-to-issue.yaml"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/todo-to-issue.yaml/badge.svg" alt="Todo to Issue"></a>
    <a href="https://github.com/adanmauri/coverage-badges/actions/workflows/dependabot/dependabot-updates"><img src="https://github.com/adanmauri/coverage-badges/actions/workflows/dependabot/dependabot-updates/badge.svg" alt="Dependabot Updates"></a>
</p>

## Table of Contents

- [Why](#why)
- [Quick Start](#quick-start)
- [Modes](#modes)
- [Supported Reports](#supported-reports)
- [Inputs and Outputs](#inputs-and-outputs)
- [How It Works](#how-it-works)
- [Command Line](#command-line)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Why

Coverage services and shields.io need to read your coverage data, so they do not work for private
repositories without handing that data to a third party. Most badge actions avoid that by pushing
the badge to the repository and linking it through `raw.githubusercontent.com`, but **that URL does
not render in the README of a private repository**: the browser has no session on that domain.

We tested every URL form in a private repository README, viewed by a logged-in user with access:

| Where the badge is served from                                               | Desktop web | GitHub mobile app |
| ---------------------------------------------------------------------------- | :---------: | :---------------: |
| `raw.githubusercontent.com/...` (and shields.io endpoints that read from it) |     ❌      |        ❌         |
| `github.com/OWNER/REPO/raw/BRANCH/...` on a dedicated branch (`branch` mode) |     ✅      |        ❌         |
| Relative path on the same branch as the README (`commit` mode)               |     ✅      |        ✅         |

This action publishes the badge in a way that renders, and prints the exact Markdown to use.

> The mobile app was tested on Android. Badges of private repositories are only visible to users
> with access to the repository, like everything else in it.

## Quick Start

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
      - run: pytest --cov --cov-report=xml
      - uses: adanmauri/coverage-badges@v1
        with:
          report: coverage.xml
```

Then add the badge to your README. The job summary prints the snippet for your repository:

```markdown
![Coverage](https://github.com/OWNER/REPO/raw/badges/coverage.svg)
```

The badge is published only from the default branch. On pull requests and other branches the action
still reads the report and sets the `coverage` output, so you can use it in later steps.

## Modes

| Mode               | Badge location                    | README snippet                                     | Trade-off                                                    |
| ------------------ | --------------------------------- | -------------------------------------------------- | ------------------------------------------------------------ |
| `branch` (default) | Orphan branch `badges`            | `![Coverage](https://github.com/OWNER/REPO/raw/badges/coverage.svg)` | Works with a protected default branch. Not shown in the mobile app. |
| `commit`           | Default branch, next to the README | `![Coverage](coverage.svg)`                       | Shown everywhere. Needs `github-actions[bot]` to be able to push to the default branch. |

```yaml
- uses: adanmauri/coverage-badges@v1
  with:
    report: coverage.xml
    mode: commit
    path: .github/badges/coverage.svg # README snippet: ![Coverage](.github/badges/coverage.svg)
```

## Supported Reports

The format is detected from the report content. Set `format` to skip detection.

| Tool                         | Command                                                     | Format        |
| ---------------------------- | ----------------------------------------------------------- | ------------- |
| pytest-cov / coverage.py     | `pytest --cov --cov-report=xml`                             | `cobertura`   |
| coverage.py                  | `coverage json`                                             | `coverage-py` |
| Jest / Vitest (Istanbul)     | `--coverage --coverageReporters=json-summary` (or `lcov`)   | `istanbul`    |
| Go                           | `go test -coverprofile=coverage.out ./...`                  | `go`          |
| JaCoCo (Gradle / Maven)      | `jacocoTestReport.xml` / `jacoco.xml`                       | `jacoco`      |
| .NET (coverlet)              | `dotnet test --collect:"XPlat Code Coverage"`               | `cobertura`   |
| Rust (cargo-llvm-cov)        | `cargo llvm-cov --lcov --output-path lcov.info`             | `lcov`        |

The badge shows line coverage (statement coverage for Go, and the coverage.py total, which includes
branches when branch coverage is enabled). The value is truncated to one decimal, so 99.96% is shown
as 99.9% and never rounded up to 100%.

## Inputs and Outputs

| Input    | Default        | Description                                                                 |
| -------- | -------------- | --------------------------------------------------------------------------- |
| `report` | (required)     | Path to the coverage report.                                                |
| `format` | `auto`         | `auto`, `cobertura`, `jacoco`, `lcov`, `go`, `coverage-py` or `istanbul`.   |
| `mode`   | `branch`       | `branch` or `commit`. See [Modes](#modes).                                  |
| `branch` | `badges`       | Branch that stores the badge in `branch` mode.                              |
| `path`   | `coverage.svg` | Path of the badge file inside the target branch.                            |
| `label`  | `Coverage`     | Text on the left side of the badge.                                         |

| Output      | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| `coverage`  | Coverage percentage shown in the badge, with one decimal (e.g. `87.5`).     |
| `published` | `true` when a new badge was pushed, `false` when unchanged or not published. |
| `markdown`  | Markdown snippet to show the badge in the README.                          |

## How It Works

- Runs on the runner's `python3` (3.10 or newer, preinstalled on GitHub-hosted Ubuntu runners;
  macOS is expected to work but not tested yet) using only the standard library. Nothing is
  installed and no data leaves GitHub.
- Builds the commit with git plumbing on a temporary index, so your checkout and working tree are
  not modified.
- Skips the commit when the badge did not change, and retries when a concurrent run pushed first.
- Commits are authored by `github-actions[bot]` and marked `[skip ci]`.
- Pushes with the credentials of `actions/checkout`, so the job needs `permissions: contents: write`.

Badge colors follow the coverage percentage: red below 40%, yellow from 40%, yellow-green from 60%
and green from 80%.

## Command Line

The badge generator also works locally. It has no dependencies, so any Python 3.10+ runs it; with
uv:

```bash
# From a coverage report
uv run python -m src.generate_badge --report coverage.xml -o coverage.svg

# From a fixed value, with a custom label
uv run python -m src.generate_badge 87.5 -l tests -o tests-coverage.svg
```

It prints the coverage value shown in the badge to stdout.

## Development

```text
coverage-badges/
├── action.yml                 # Composite GitHub Action
├── scripts/
│   └── publish-badge.sh       # Pushes the badge to a branch without touching the checkout
├── src/
│   ├── badge_generator.py     # SVG generation
│   ├── coverage_report.py     # Report parsers and format detection
│   └── generate_badge.py      # CLI used by the action
└── tests/
    ├── fixtures/              # One sample report per supported format
    └── test_*.py
```

```bash
make setup   # once per clone: uv sync, then the pre-commit and commit-msg hooks (needs uv)
make check   # hooks over the whole repo, then the tests on Python 3.14 and 3.10
make help    # every target
```

The test suite runs `publish-badge.sh` against a local bare repository, so it needs `git`. The CI
also runs the action on this repository to publish its own badge, and checks the generator with the
system Python 3.10 of Ubuntu 22.04. CI lints and scans with MegaLinter, at the same linter
versions as the local hooks; see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#quality-gates).

AI agents follow [AGENTS.md](AGENTS.md), with rules and skills under [`.agents/`](.agents/README.md).
See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
