#!/usr/bin/env python3
"""Generate the vendor pointers for the canonical agent assets under .agents/.

Skills (.agents/skills/{id}/SKILL.md) get a pointer in each vendor skill directory.
Rules and context (.agents/{rules,context}/{stem}.md) get an always-on pointer for
Cursor and GitHub Copilot. Pointers carry only frontmatter and a link, never logic.

Usage:
    uv run --no-project tooling/sync_agents.py          # write pointers, prune orphaned ones
    uv run --no-project tooling/sync_agents.py --check  # write nothing, exit 1 on drift

Stdlib only. See .agents/README.md.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / ".agents"

SKILL_VENDORS = [ROOT / ".claude" / "skills", ROOT / ".github" / "skills"]
SKILL_MARKER = "**Source of truth:** The full instructions for this skill live in"
RULE_MARKER = "**Source of truth:** the authoritative version of this rule lives in"
RULE_KINDS = ["rules", "context"]


def parse(path: Path) -> tuple[dict[str, str], str]:
    """Return (frontmatter fields, first H1 title) of a Markdown file."""
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    body = text
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if match:
        body = text[match.end() :]
        for line in match.group(1).splitlines():
            key, sep, value = line.partition(":")
            if sep:
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                fields[key.strip()] = value
    title = re.search(r"^# (.+)$", body, re.M)
    return fields, title.group(1).strip() if title else path.stem


def yaml_str(value: str) -> str:
    """Quote a scalar only when plain YAML would misread it."""
    if ": " in value or value.startswith(("'", '"', "[", "{", "*", "&", "!", "|", ">")):
        return json.dumps(value, ensure_ascii=False)
    return value


def skill_pointers() -> dict[Path, str]:
    """Pointer path and content for every canonical skill, per vendor."""
    out: dict[Path, str] = {}
    for canonical in sorted((AGENTS / "skills").glob("*/SKILL.md")):
        skill_id = canonical.parent.name
        fields, title = parse(canonical)
        if fields.get("name") != skill_id or not fields.get("description"):
            sys.exit(f"{canonical}: frontmatter needs name == '{skill_id}' and a description")
        content = (
            "---\n"
            f"name: {skill_id}\n"
            f"description: {yaml_str(fields['description'])}\n"
            "---\n\n"
            f"# {title}\n\n"
            f"{SKILL_MARKER}\n"
            f"[`.agents/skills/{skill_id}/SKILL.md`]"
            f"(../../../.agents/skills/{skill_id}/SKILL.md).\n\n"
            "When this skill is invoked, read that file and follow its instructions completely.\n"
        )
        for vendor in SKILL_VENDORS:
            out[vendor / skill_id / "SKILL.md"] = content
    return out


def rule_pointers() -> dict[Path, str]:
    """Pointer path and content for every rule and context file, per tool."""
    out: dict[Path, str] = {}
    for kind in RULE_KINDS:
        for canonical in sorted((AGENTS / kind).glob("*.md")):
            fields, title = parse(canonical)
            if not fields.get("description"):
                sys.exit(f"{canonical}: frontmatter needs a description")
            rel = f".agents/{kind}/{canonical.name}"
            link = f"{RULE_MARKER}\n[`{rel}`](../../{rel}). Read it and follow it completely.\n"
            out[ROOT / ".cursor" / "rules" / f"{canonical.stem}.mdc"] = (
                "---\n"
                f"description: {yaml_str(fields['description'])}\n"
                "alwaysApply: true\n"
                "---\n\n"
                f"# {title}\n\n{link}"
            )
            out[ROOT / ".github" / "instructions" / f"{canonical.stem}.instructions.md"] = (
                f"---\napplyTo: '**'\n---\n\n# {title}\n\n{link}"
            )
    return out


def orphans(expected: dict[Path, str]) -> list[Path]:
    """Generated pointers (identified by their marker) whose canonical is gone."""
    found: list[Path] = []
    candidates = [p for v in SKILL_VENDORS for p in v.glob("*/SKILL.md")]
    candidates += list((ROOT / ".cursor" / "rules").glob("*.mdc"))
    candidates += list((ROOT / ".github" / "instructions").glob("*.instructions.md"))
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        if path not in expected and (SKILL_MARKER in text or RULE_MARKER in text):
            found.append(path)
    return sorted(found)


def main() -> int:
    """Write the pointers, or report drift with --check."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = parser.parse_args()

    expected = {**skill_pointers(), **rule_pointers()}
    stale = [p for p, c in expected.items() if not p.exists() or p.read_text(encoding="utf-8") != c]
    extra = orphans(expected)

    for path in stale:
        print(f"{'out of sync' if args.check else 'write'}: {path.relative_to(ROOT)}")
    for path in extra:
        print(f"{'orphaned' if args.check else 'prune'}: {path.relative_to(ROOT)}")

    if args.check:
        if stale or extra:
            print("Agent pointers are out of sync: run `make sync-agents`.")
            return 1
        print(f"Agent pointers in sync ({len(expected)} files).")
        return 0

    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected[path], encoding="utf-8")
    for path in extra:
        if path.name == "SKILL.md" and len(list(path.parent.iterdir())) == 1:
            shutil.rmtree(path.parent)
        else:
            path.unlink()
    print(f"Done: {len(stale)} written, {len(extra)} pruned, {len(expected)} total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
