#!/usr/bin/env python3
"""commit-msg hook: reject tool attribution in a commit message.

The commit author owns the change; no tool is credited in it (see the create-commit skill).
Only attribution patterns are matched, so a message that mentions `.claude/`, `CLAUDE.md` or a
CSS cursor is fine; a `Co-Authored-By:` trailer naming an assistant is not.

Usage (wired by pre-commit at the commit-msg stage):
    uv run --no-project tooling/check_commit_msg.py <commit-message-file>

Stdlib only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOOLS = r"(claude|anthropic|cursor|copilot|chatgpt|openai|codex|gemini|bard|llm)"

FORBIDDEN = [
    re.compile(rf"^\s*co-authored-by:.*{TOOLS}", re.IGNORECASE),
    re.compile(rf"^\s*signed-off-by:.*{TOOLS}", re.IGNORECASE),
    re.compile(r"\b(generated|made|created|written) (with|by|using) .*" + TOOLS, re.IGNORECASE),
    re.compile(r"noreply@(anthropic|openai|cursor)\.", re.IGNORECASE),
    re.compile("\N{ROBOT FACE}"),
]


def offending_lines(text: str) -> list[str]:
    """Lines of a commit message that credit a tool; git's own '#' comment lines are skipped."""
    return [
        line
        for line in text.splitlines()
        if not line.startswith("#") and any(p.search(line) for p in FORBIDDEN)
    ]


def main() -> int:
    """Check the commit message file given as the only argument."""
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    offenders = offending_lines(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not offenders:
        return 0
    print(
        "Commit rejected: remove the tool attribution from the message (see create-commit).",
        file=sys.stderr,
    )
    for line in offenders:
        print(f"  {line}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
