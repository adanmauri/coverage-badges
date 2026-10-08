#!/usr/bin/env python3
"""Fail when the docs stop matching the repo they describe.

Two checks, each a silent failure that a Markdown linter does not catch:

- links: every relative Markdown link (inline or reference-style) points at a file or folder
  that exists. External URLs and pure anchors are not checked.
- adr: the ADR set and its index agree. Files are `NNNN-<slug>.md` with the H1 `# NNNN. <Title>`,
  numbers have no gaps or duplicates (a number taken by an open branch is listed under
  `## Reserved` in the index), and the index links every ADR.

Usage:
    uv run --no-project tooling/check_docs.py

Stdlib only. Ported from the owner's boxytrack repository, without its ticket-ID check.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = ROOT / "docs" / "adr"
ADR_INDEX = ADR_DIR / "README.md"

SKIP_DIRS = {".git", ".venv", "node_modules", "megalinter-reports"}

FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
CODE_RE = re.compile(r"`[^`\n]*`")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
INLINE_LINK_RE = re.compile(r"\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
REF_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)", re.M)
EXTERNAL_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
ADR_FILE_RE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
ADR_H1_RE = re.compile(r"^# (\d{4})\. \S", re.M)
RESERVED_RE = re.compile(r"^## Reserved$(.*?)(?=^## |\Z)", re.M | re.S)


def markdown_files() -> Iterator[Path]:
    """Every Markdown file in the repository, outside generated or vendored trees."""
    for path in sorted(ROOT.rglob("*.md")):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def rel(path: Path) -> str:
    """Path relative to the repository root, with forward slashes."""
    return path.relative_to(ROOT).as_posix()


def prose(text: str) -> str:
    """The text without fenced blocks, inline code and HTML comments, where links are examples."""
    return CODE_RE.sub("", COMMENT_RE.sub("", FENCE_RE.sub("", text)))


def check_links() -> list[str]:
    """Relative links whose target does not exist."""
    errors = []
    for path in markdown_files():
        text = prose(path.read_text(encoding="utf-8"))
        targets = INLINE_LINK_RE.findall(text) + REF_LINK_RE.findall(text)
        for target in targets:
            if EXTERNAL_RE.match(target) or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if clean and not (path.parent / clean).exists():
                errors.append(f"{rel(path)}: broken link '{target}'")
    return errors


def check_adrs() -> list[str]:
    """Numbering, headings and index entries of the ADRs that disagree."""
    errors = []
    files = sorted(p for p in ADR_DIR.glob("*.md") if ADR_FILE_RE.match(p.name))
    numbers: list[int] = []
    for path in files:
        match = ADR_FILE_RE.match(path.name)
        assert match is not None  # files were filtered by this pattern
        number = int(match.group(1))
        h1 = ADR_H1_RE.search(path.read_text(encoding="utf-8"))
        if not h1:
            errors.append(f"{rel(path)}: first heading must be '# {number:04d}. <Title>'")
        elif int(h1.group(1)) != number:
            errors.append(f"{rel(path)}: file says {number:04d}, heading says {h1.group(1)}")
        if number in numbers:
            errors.append(f"{rel(path)}: number {number:04d} is used twice")
        numbers.append(number)
    index = ADR_INDEX.read_text(encoding="utf-8") if ADR_INDEX.exists() else ""
    reserved_block = RESERVED_RE.search(index)
    reserved = (
        {int(n) for n in re.findall(r"`(\d{4})`", reserved_block.group(1))}
        if reserved_block
        else set()
    )
    for n in range(1, max(numbers, default=0)):
        if n not in numbers and n not in reserved:
            errors.append(f"docs/adr: number {n:04d} is missing and not listed under '## Reserved'")
    for path in files:
        if f"]({path.name})" not in index:
            errors.append(f"docs/adr/README.md: does not link {path.name}")
    return errors


def main() -> int:
    """Run both checks and report every error found."""
    errors = check_links() + check_adrs()
    if errors:
        print("\n".join(errors))
        print(f"{len(errors)} docs error(s).")
        return 1
    print("Docs OK: links and ADR index.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
