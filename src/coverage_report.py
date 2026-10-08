"""Coverage report parsing.

This module reads the total coverage percentage from the report formats
produced by the most common coverage tools, using only the standard library
so the GitHub Action runs on the runner's Python without installing anything.

Supported formats are Cobertura XML, JaCoCo XML, LCOV, Go coverprofile,
coverage.py JSON and Istanbul json-summary. The format can be detected
automatically from the report content.
"""

import json

# Reports are the user's own CI artifacts, not untrusted input.
import xml.etree.ElementTree as ET  # nosec B405
from collections.abc import Callable
from pathlib import Path
from typing import Any

FORMATS = ("cobertura", "jacoco", "lcov", "go", "coverage-py", "istanbul")


def _percent(covered: float, total: float) -> float:
    """Convert covered and total counts to a percentage."""
    if total <= 0:
        raise ValueError("The coverage report does not contain any coverable lines")
    return covered / total * 100


def _parse_xml(content: str) -> ET.Element:
    """Parse XML report content."""
    try:
        return ET.fromstring(content)  # nosec B314
    except ET.ParseError as error:
        raise ValueError(f"Invalid XML coverage report: {error}") from error


def _parse_json(content: str) -> dict[str, Any]:
    """Parse JSON report content."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON coverage report: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON coverage report: expected an object")  # noqa: TRY004
    return data


def parse_cobertura(content: str) -> float:
    """Read line coverage from a Cobertura XML report."""
    root = _parse_xml(content)
    line_rate = root.get("line-rate")
    if root.tag != "coverage" or line_rate is None:
        raise ValueError("Not a Cobertura report: missing <coverage line-rate>")
    return float(line_rate) * 100


def parse_jacoco(content: str) -> float:
    """Read line coverage from a JaCoCo XML report."""
    root = _parse_xml(content)
    if root.tag != "report":
        raise ValueError("Not a JaCoCo report: missing <report> root")
    for counter in root.findall("counter"):
        if counter.get("type") == "LINE":
            covered = int(counter.get("covered", "0"))
            missed = int(counter.get("missed", "0"))
            return _percent(covered, covered + missed)
    raise ValueError("Not a JaCoCo report: missing report-level LINE counter")


def parse_lcov(content: str) -> float:
    """Read line coverage from an LCOV tracefile.

    Uses the LF/LH summary of each record and falls back to counting the DA
    entries for records that do not include the summary.
    """
    found = hit = 0
    record_found = record_hit = da_found = da_hit = 0
    has_summary = False
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("LF:"):
            record_found, has_summary = int(line[3:]), True
        elif line.startswith("LH:"):
            record_hit = int(line[3:])
        elif line.startswith("DA:"):
            da_found += 1
            if int(line[3:].split(",")[1]) > 0:
                da_hit += 1
        elif line == "end_of_record":
            found += record_found if has_summary else da_found
            hit += record_hit if has_summary else da_hit
            record_found = record_hit = da_found = da_hit = 0
            has_summary = False
    return _percent(hit, found)


def parse_go(content: str) -> float:
    """Read statement coverage from a Go coverprofile.

    Blocks that appear more than once (for example with -coverpkg) are counted
    once and considered covered if any occurrence was executed.
    """
    blocks: dict[str, tuple[int, bool]] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("mode:"):
            continue
        try:
            block, statements, count = line.rsplit(" ", 2)
            covered = int(count) > 0
            previous = blocks.get(block, (int(statements), False))
            blocks[block] = (previous[0], previous[1] or covered)
        except ValueError as error:
            raise ValueError(f"Invalid Go coverprofile line: {line!r}") from error
    total = sum(statements for statements, _ in blocks.values())
    covered_total = sum(statements for statements, covered in blocks.values() if covered)
    return _percent(covered_total, total)


def parse_coverage_py(content: str) -> float:
    """Read the total from a coverage.py JSON report."""
    totals = _parse_json(content).get("totals")
    if not isinstance(totals, dict) or "percent_covered" not in totals:
        raise ValueError("Not a coverage.py report: missing totals.percent_covered")
    return float(totals["percent_covered"])


def parse_istanbul(content: str) -> float:
    """Read line coverage from an Istanbul json-summary report."""
    total = _parse_json(content).get("total")
    lines = total.get("lines") if isinstance(total, dict) else None
    if not isinstance(lines, dict) or "covered" not in lines or "total" not in lines:
        raise ValueError("Not an Istanbul json-summary report: missing total.lines")
    return _percent(lines["covered"], lines["total"])


PARSERS: dict[str, Callable[[str], float]] = {
    "cobertura": parse_cobertura,
    "jacoco": parse_jacoco,
    "lcov": parse_lcov,
    "go": parse_go,
    "coverage-py": parse_coverage_py,
    "istanbul": parse_istanbul,
}


def detect_format(content: str) -> str:
    """Detect the report format from its content."""
    text = content.lstrip()
    if text.startswith("<"):
        tag = _parse_xml(content).tag
        if tag == "coverage":
            return "cobertura"
        if tag == "report":
            return "jacoco"
    elif text.startswith("{"):
        data = _parse_json(content)
        if "totals" in data:
            return "coverage-py"
        if "total" in data:
            return "istanbul"
    elif text.startswith("mode:"):
        return "go"
    elif "end_of_record" in text:
        return "lcov"
    raise ValueError(
        f"Could not detect the coverage report format. Set it explicitly: {', '.join(FORMATS)}"
    )


def read_coverage(report: Path, report_format: str = "auto") -> float:
    """Read the total coverage percentage from a report file."""
    if report_format != "auto" and report_format not in PARSERS:
        raise ValueError(f"Unknown report format {report_format!r}. Use auto or one of: {FORMATS}")
    content = report.read_text(encoding="utf-8")
    if report_format == "auto":
        report_format = detect_format(content)
    return PARSERS[report_format](content)
