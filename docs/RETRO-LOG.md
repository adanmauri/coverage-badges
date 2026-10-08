# Retro log

One entry per session retrospective (see the `retro` skill), newest first.

## 2026-10-08: CI checks what changed, at the versions the hooks use

- **Context:** reviewed the CI items left in `TODO.md` (the broken Trivy job, `MEGALINTER_CACHE`,
  which MegaLinter linters block); the owner asked for pull requests to check only what changed
  and for the local linters to match MegaLinter's versions.
- **Changes:**
  - The broken Trivy job had gone into `TODO.md` as "the tag no longer exists, pin a newer one".
    Asked why, the tag turned out to be one of those rewritten in the March 2026 `trivy-action`
    compromise, and this repository's run had used it inside the window → ADR-0009, and the
    workflow rules in the coding standards (a vanished tag is a signal).
  - ADR-0004 said MegaLinter's image had no uv, and the pre-commands installed pytest into the
    system Python. The Dockerfile shows uv in the image and one venv per Python linter, so the
    pre-commands could not reach mypy or pylint → the rule to read the container's Dockerfile, and
    the pre-commands now target each linter's venv.
  - MegaLinter used its default config files instead of `pyproject.toml` for four Python linters,
    and versions apart from the lock → ADR-0007, `tooling/check_linter_versions.py`.
- **Follow-ups:** the first MegaLinter v10.1.0 run on GitHub, and running its image by digest, are
  in `TODO.md`.

## 2026-10-07: pivot to a GitHub Action, and an agent harness to go with it

- **Context:** turned the collection of pre-generated badges into a GitHub Action for private
  repositories, after verifying in a throwaway private repository which badge URLs render there.
- **Changes:**
  - A commit carried a `Co-Authored-By` trailer naming the assistant, against the owner's rule in
    their other repositories → `no-tool-attribution` commit-msg hook and the `create-commit` skill.
  - The badge generator used Python 3.12 f-string syntax and failed on 3.9 and 3.10, which the
    action has to support → `make test-compat`, the runtime section of the action guardrails, and
    a CI job on the system Python of Ubuntu 22.04.
  - The first answer about alternatives and URL forms came from memory and two claims were wrong;
    a real private repository settled it → `AGENTS.md` Verification section and the badge URL
    rules in the action guardrails.
  - An agent cannot see a private README rendered; the owner checked desktop and mobile by hand →
    Verification step 2 says so, so rendering is never reported as verified without a person.
  - A command failed because zsh does not split unquoted variables → shell rule in the coding
    standards.
  - A commit went out with a pyright error that MegaLinter would have failed in CI, because
    `make check` had no type checkers → mypy, pyright, pylint and bandit run as local hooks.
  - `.cursorrules` belonged to another project and the README promised pre-commit hooks that did
    not exist → `.agents/rules/`, `.pre-commit-config.yaml` and `make check`.
- **Follow-ups:** tests ran through `uv` while dependencies were declared in Pipenv; the owner
  asked to move everything to uv, done right after. The iOS rendering check and the `v1` release
  are in `TODO.md`.
