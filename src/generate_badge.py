"""Script to generate coverage SVG badges.

This script generates coverage SVG badges that can be imported
in README.md files of other GitHub projects. The badges are generated
with different coverage levels and colors according to the percentage.
"""

import argparse
import logging
from pathlib import Path

from src.badge_generator import BadgeGenerator

logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to generate badges."""
    parser = argparse.ArgumentParser(description="Generate coverage SVG badges.")
    parser.add_argument("coverage", type=float, help="Coverage percentage (0-100).")
    parser.add_argument("-o", "--output", type=str, help="Output file (default: badge.svg).")
    parser.add_argument(
        "-l",
        "--label",
        type=str,
        default="Coverage",
        help="Badge label (default: Coverage).",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default="badges",
        help="Directory to save the badge (default: badges).",
    )

    args = parser.parse_args()
    output_dir = Path(args.directory)
    output_dir.mkdir(exist_ok=True)
    if args.output:
        output_file = output_dir / args.output
    else:
        coverage_int = int(args.coverage)
        output_file = output_dir / f"coverage-{coverage_int}.svg"
    badge_generator = BadgeGenerator()
    badge_path = badge_generator.generate_and_save_badge(
        float(args.coverage), output_file, args.label
    )
    logger.info("Badge generated and saved to %s", badge_path)


if __name__ == "__main__":
    main()
