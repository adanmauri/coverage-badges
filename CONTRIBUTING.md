# Contributing to Coverage Badges

Thank you for your interest in contributing to Coverage Badges! This document covers the
contribution process. How to set up, check and change the code is in
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md), and the binding coding standards are in
[`.agents/rules/`](.agents/rules/).

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-user>/coverage-badges.git`
3. Set up the development environment (needs [uv](https://docs.astral.sh/uv/)):

   ```bash
   make setup   # uv sync --locked, then installs the git hooks
   ```

## Reporting Issues

- Before opening a new issue, search for existing issues to avoid duplicates
- Include minimal examples when reporting bugs: the workflow step, the coverage report format and,
  if you can, a trimmed report that reproduces it
- Include relevant information:
  - Runner OS and the `python3 --version` it ships
  - Whether the repository is private, and the `mode` used
  - Steps to reproduce
  - Expected vs actual behavior

## Contributing Code

### For New Contributors

If you're new to the project and would like guidance on where to start, feel free to:

- Open an issue asking for suggestions
- Comment on existing issues to express interest
- Start with small improvements like documentation or bug fixes

### Development Workflow

1. Create a branch from an up-to-date `main`: `feat/...`, `fix/...`, `docs/...` or `chore/...`
2. Make your changes following the [coding standards](.agents/rules/coding-standards.md) and, for
   `action.yml`, `scripts/` and `src/`, the [action guardrails](.agents/rules/action-guardrails.md)
3. Add or update tests (see [Testing](docs/DEVELOPMENT.md#testing))
4. Run `make check` until it passes; the commit hook runs the same linters on staged files
5. Commit with [Conventional Commits](https://www.conventionalcommits.org/):
   `feat(parser): read Clover reports`, `fix(publish): retry on a rejected push`
6. Push to your fork and open a Pull Request

A change that affects how the badge is published or which URL it uses also needs the rendering
check in a private repository described in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#where-the-badge-is-published).

### Pull Request Guidelines

- **All PRs should be opened against the `main` branch**
- Fill the PR template; under Test plan, list only what you actually ran
- Aim for atomic commits (one logical change per commit)
- If your PR changes inputs, outputs or badge URLs for users pinned to `@v1`, say so in the title
  with `!` (`feat(action)!: ...`) and explain it under Notes
- Keep PRs focused: avoid mixing unrelated changes
- If a PR is not ready for review, mark it as a Draft
- Update the README, `action.yml` descriptions and docs when you change behavior

### Git Best Practices

- Avoid working directly on the `main` branch of your fork
- Use `git add -p` to stage changes selectively
- If conflicts arise, prefer `git rebase` over `git merge` to keep history clean
- When linking to code in discussions, use GitHub's permalink feature (press `y` while viewing code)

### Decisions

A change that reverses or extends a recorded decision (publishing modes, runtime, toolchain,
quality gates) comes with a new ADR in [docs/adr/](docs/adr/README.md), from the template there.

## Code Review Process

1. All PRs require at least one approval before merging
2. Maintainers will review code for:
   - Adherence to the coding standards and action guardrails
   - Code quality and correctness
   - Test coverage
   - Documentation updates
3. Address review comments promptly
4. Keep discussions focused and constructive

## Questions?

If you have questions or need help, feel free to:

- Open an issue with the `question` label
- Comment on existing issues or PRs
- Reach out to maintainers

Thank you for contributing to Coverage Badges!
