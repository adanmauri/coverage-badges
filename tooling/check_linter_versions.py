#!/usr/bin/env python3
"""Fail when a local linter version differs from the one in the MegaLinter image CI runs.

CI lints with the linters bundled in the MegaLinter image that code-quality.yaml pins by commit;
the local hooks lint with the versions in pyproject.toml (Python linters, through uv.lock) and
.pre-commit-config.yaml (the rest). When the two drift, a file can pass locally and fail in CI.
This reads the image's Dockerfile at the pinned commit and compares every linter that runs in
both places (docs/adr/0007).

Usage:
    uv run --no-project tooling/check_linter_versions.py

Stdlib only. Needs network access to raw.githubusercontent.com.
"""

from __future__ import annotations

import re
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "code-quality.yaml"
PYPROJECT = ROOT / "pyproject.toml"
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"

DOCKERFILE_URL = (
    "https://raw.githubusercontent.com/oxsecurity/megalinter/{ref}/flavors/python/Dockerfile"
)

MEGALINTER_RE = re.compile(r"uses: oxsecurity/megalinter/flavors/python@([0-9a-f]{40})\b")
ARG_RE = re.compile(r"^ARG ([A-Z0-9_]+)=(\S+)$", re.MULTILINE)
PIN_RE = re.compile(r"^([A-Za-z0-9_.-]+)==(\S+)$")
HOOK_REPO_RE = re.compile(r"^\s*- repo: (\S+)\n\s+rev: (\S+)$", re.MULTILINE)

# Python package pinned in pyproject.toml -> Dockerfile ARG holding the image's version.
PACKAGES = {
    "bandit": "PIP_BANDIT_VERSION",
    "black": "PIP_BLACK_VERSION",
    "flake8": "PIP_FLAKE8_VERSION",
    "isort": "PIP_ISORT_VERSION",
    "mypy": "PIP_MYPY_VERSION",
    "pylint": "PIP_PYLINT_VERSION",
    "pyright": "NPM_PYRIGHT_VERSION",
    "ruff": "PIP_RUFF_VERSION",
}

# pre-commit hook repository -> Dockerfile ARG holding the image's version.
HOOK_REPOS = {
    "https://github.com/rhysd/actionlint": "ACTION_ACTIONLINT_VERSION",
    "https://github.com/shellcheck-py/shellcheck-py": "BASH_SHELLCHECK_VERSION",
    "https://github.com/zizmorcore/zizmor-pre-commit": "CARGO_ZIZMOR_VERSION",
}


def same_version(local: str, image: str) -> bool:
    """Compare ignoring a `v` prefix; a wrapper may add a fourth part (shellcheck-py 0.11.0.1)."""
    local, image = local.removeprefix("v"), image.removeprefix("v")
    return local == image or local.startswith(image + ".")


def megalinter_ref() -> str:
    """The commit the MegaLinter step in code-quality.yaml is pinned to."""
    match = MEGALINTER_RE.search(WORKFLOW.read_text(encoding="utf-8"))
    if not match:
        sys.exit(f"{WORKFLOW.relative_to(ROOT)}: no MegaLinter step pinned to a commit SHA.")
    return match.group(1)


def image_versions(ref: str) -> dict[str, str]:
    """Every `ARG NAME=value` in the flavor's Dockerfile at that commit."""
    url = DOCKERFILE_URL.format(ref=ref)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            dockerfile = response.read().decode("utf-8")
    except urllib.error.URLError as error:
        sys.exit(f"Cannot read the MegaLinter Dockerfile at {url}: {error}")
    versions: dict[str, str] = {}
    for name, value in ARG_RE.findall(dockerfile):
        versions.setdefault(name, value)
    return versions


def pinned_packages() -> dict[str, str]:
    """`name==version` requirements across the dependency groups of pyproject.toml."""
    groups = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["dependency-groups"]
    pins: dict[str, str] = {}
    for requirements in groups.values():
        for requirement in requirements:
            match = PIN_RE.match(requirement) if isinstance(requirement, str) else None
            if match:
                pins[match.group(1).lower()] = match.group(2)
    return pins


def hook_revs() -> dict[str, str]:
    """The rev of every hook repository in .pre-commit-config.yaml."""
    return dict(HOOK_REPO_RE.findall(PRE_COMMIT.read_text(encoding="utf-8")))


def compare(label: str, source: str, local: str | None, arg: str, image: dict[str, str]) -> str:
    """An error line when the local version is missing or differs from the image, else ""."""
    if arg not in image:
        return f"{label}: the MegaLinter image has no {arg}; update this script or {source}."
    if local is None:
        return f"{label}: not pinned in {source}; MegaLinter has {image[arg]}."
    if not same_version(local, image[arg]):
        return f"{label}: {local} in {source}, {image[arg]} in MegaLinter."
    return ""


def main() -> int:
    """Print every difference and return 1 if there is any."""
    ref = megalinter_ref()
    image = image_versions(ref)
    pins, revs = pinned_packages(), hook_revs()
    errors = [
        compare(package, "pyproject.toml", pins.get(package), arg, image)
        for package, arg in PACKAGES.items()
    ] + [
        compare(repo.rsplit("/", 1)[1], ".pre-commit-config.yaml", revs.get(repo), arg, image)
        for repo, arg in HOOK_REPOS.items()
    ]
    errors = [error for error in errors if error]
    if errors:
        print("\n".join(errors))
        print(f"{len(errors)} linter version(s) differ from MegaLinter {ref[:12]}.")
        return 1
    print(f"Linter versions match MegaLinter {ref[:12]}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
