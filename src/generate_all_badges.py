"""Script to generate pre-made badges with different coverage levels.

Generates SVG badges for coverage levels from 0% to 100% in 5% increments,
so they can be easily imported in other projects.
"""

import logging
from pathlib import Path

from src.badge_generator import BadgeGenerator

logger = logging.getLogger(__name__)


def main() -> None:
    """Generate badges for all coverage levels."""
    badges_dir = Path("badges")
    badges_dir.mkdir(exist_ok=True)

    for coverage in range(0, 101, 5):
        output_file = badges_dir / f"coverage-{coverage}.svg"
        badge_generator = BadgeGenerator()
        badge_path = badge_generator.generate_and_save_badge(float(coverage), output_file)
        logger.info("Badge generated and saved to %s", badge_path)


if __name__ == "__main__":
    main()
