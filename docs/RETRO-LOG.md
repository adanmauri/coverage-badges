# Retro log

One entry per session retrospective (see the `retro` skill), newest first.

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
  - `.cursorrules` belonged to another project and the README promised pre-commit hooks that did
    not exist → `.agents/rules/`, `.pre-commit-config.yaml` and `make check`.
- **Follow-ups:** tests run through `uv` while dependencies are still declared in Pipenv; moving
  the project to uv, like the owner's other repositories, is a separate decision. The iOS rendering
  check and the `v1` release are in `TODO.md`.
