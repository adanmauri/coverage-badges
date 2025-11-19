"""Package to generate coverage SVG badges.

This package provides a BadgeGenerator class and CLI tools to generate
coverage SVG badges that can be imported in README.md files of GitHub projects.
"""

from src.badge_generator import BadgeGenerator

__all__ = ["BadgeGenerator"]
