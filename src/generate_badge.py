"""Script to generate coverage SVG badges.

This script generates a coverage SVG badge either from a fixed percentage or
from a coverage report (Cobertura, JaCoCo, LCOV, Go, coverage.py or Istanbul).
It prints the coverage percentage shown in the badge to stdout, so it can be
captured by the GitHub Action or any other CI script.
"""

import argparse
import logging
import math
from pathlib import Path

from src.badge_generator import BadgeGenerator
from src.coverage_report import FORMATS, read_coverage

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Main function to generate a badge."""
    parser = argparse.ArgumentParser(description="Generate a coverage SVG badge.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("coverage", type=float, nargs="?", help="Coverage percentage (0-100).")
    source.add_argument("-r", "--report", type=Path, help="Coverage report to read the value from.")
    parser.add_argument(
        "-f",
        "--format",
        choices=("auto", *FORMATS),
        default="auto",
        help="Report format (default: auto).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("coverage.svg"),
        help="Output file (default: coverage.svg).",
    )
    parser.add_argument(
        "-l",
        "--label",
        type=str,
        default="Coverage",
        help="Badge label (default: Coverage).",
    )

    args = parser.parse_args(argv)
    if args.report is not None:
        try:
            coverage = read_coverage(args.report, args.format)
        except (OSError, ValueError) as error:
            parser.exit(1, f"error: {error}\n")
    else:
        coverage = args.coverage
    # Truncate instead of rounding so the badge never overstates coverage (99.96 -> 99.9).
    coverage = math.floor(round(coverage * 10, 6)) / 10

    try:
        badge_path = BadgeGenerator().generate_and_save_badge(coverage, args.output, args.label)
    except ValueError as error:
        parser.exit(1, f"error: {error}\n")
    logger.info("Badge generated and saved to %s", badge_path)
    print(f"{coverage:.1f}")


if __name__ == "__main__":
    main()
