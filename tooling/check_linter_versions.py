#!/usr/bin/env python3
"""Fail when a pre-commit hook's linter version differs from the one in the MegaLinter image.

CI lints with the linters bundled in the MegaLinter image that code-quality.yaml pins by commit.
The non-Python hooks in .pre-commit-config.yaml pin a version of their own (a hook repository's
rev, or the Node.js and Go packages a local hook installs), and that version is the image's, so a
file that passes the hook passes the same linter in CI. This reads the image's Dockerfile at the
pinned commit and compares them (docs/adr/0007). The Python linters run from uv.lock and are not
compared.

Usage:
    uv run --no-project tooling/check_linter_versions.py

Stdlib only. Needs network access to raw.githubusercontent.com.
"""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "code-quality.yaml"
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"

DOCKERFILE_URL = (
    "https://raw.githubusercontent.com/oxsecurity/megalinter/{ref}/flavors/python/Dockerfile"
)

MEGALINTER_RE = re.compile(r"uses: oxsecurity/megalinter/flavors/python@([0-9a-f]{40})\b")
ARG_RE = re.compile(r"^ARG ([A-Z0-9_]+)=(\S+)$", re.MULTILINE)
HOOK_REPO_RE = re.compile(r"^\s*- repo: (\S+)\n\s+rev: (\S+)$", re.MULTILINE)
DEPENDENCIES_RE = re.compile(r"^(\s*)additional_dependencies:(.*)$")
# The image's ARG values carry the base image of a tool, or its Alpine package revision.
IMAGE_SUFFIX_RE = re.compile(r"-(alpine|r\d+)$")

# pre-commit hook repository -> Dockerfile ARG holding the image's version.
HOOK_REPOS = {
    "https://github.com/betterleaks/betterleaks": "REPOSITORY_BETTERLEAKS_VERSION",
    "https://github.com/rhysd/actionlint": "ACTION_ACTIONLINT_VERSION",
    "https://github.com/shellcheck-py/shellcheck-py": "BASH_SHELLCHECK_VERSION",
    "https://github.com/zizmorcore/zizmor-pre-commit": "CARGO_ZIZMOR_VERSION",
}

# Node.js or Go package a local hook installs (additional_dependencies) -> Dockerfile ARG.
HOOK_DEPENDENCIES = {
    "@prantlf/jsonlint": "NPM_PRANTLF_JSONLINT_VERSION",
    "@secretlint/secretlint-rule-preset-recommend": (
        "NPM_SECRETLINT_SECRETLINT_RULE_PRESET_RECOMMEND_VERSION"
    ),
    "cspell": "NPM_CSPELL_VERSION",
    "jscpd": "NPM_JSCPD_VERSION",
    "markdown-table-formatter": "NPM_MARKDOWN_TABLE_FORMATTER_VERSION",
    "markdownlint-cli": "NPM_MARKDOWNLINT_CLI_VERSION",
    "mvdan.cc/sh/v3/cmd/shfmt": "BASH_SHFMT_VERSION",
    "prettier": "NPM_PRETTIER_VERSION",
    "secretlint": "NPM_SECRETLINT_VERSION",
}


def same_version(local: str, image: str) -> bool:
    """Compare ignoring a `v` prefix and the image's suffix (`-alpine`, `-r1`); a wrapper may add
    a fourth part (shellcheck-py 0.11.0.1)."""
    local, image = local.removeprefix("v"), IMAGE_SUFFIX_RE.sub("", image.removeprefix("v"))
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


def hook_revs() -> dict[str, str]:
    """The rev of every hook repository in .pre-commit-config.yaml."""
    return dict(HOOK_REPO_RE.findall(PRE_COMMIT.read_text(encoding="utf-8")))


def hook_dependencies() -> dict[str, str]:
    """`name@version` entries of every additional_dependencies list, inline or one per line."""
    pins: dict[str, str] = {}
    lines = PRE_COMMIT.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        match = DEPENDENCIES_RE.match(line)
        if not match:
            continue
        indent, inline = match.groups()
        if inline.strip():
            items = inline.strip().strip("[]").split(",")
        else:
            items = []
            for item in lines[index + 1 :]:
                if not item.startswith(indent + " ") or not item.strip().startswith("- "):
                    break
                items.append(item.strip().removeprefix("- "))
        for item in items:
            name, _, version = item.strip().strip("\"'").rpartition("@")
            if name:
                pins[name] = version
    return pins


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
    revs, dependencies = hook_revs(), hook_dependencies()
    errors = [
        compare(repo.rsplit("/", 1)[1], ".pre-commit-config.yaml", revs.get(repo), arg, image)
        for repo, arg in HOOK_REPOS.items()
    ] + [
        compare(name, ".pre-commit-config.yaml", dependencies.get(name), arg, image)
        for name, arg in HOOK_DEPENDENCIES.items()
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
