"""Tests for BadgeGenerator class."""

from pathlib import Path

import pytest

from src.badge_generator import BadgeGenerator


# pylint: disable=too-few-public-methods
class TestBadgeGeneratorInit:
    """Test suite for BadgeGenerator initialization."""

    def test_init(self) -> None:
        """Test BadgeGenerator initialization."""
        generator = BadgeGenerator()
        assert generator is not None


# pylint: disable=too-few-public-methods
class TestBadgeGeneratorColorGradient:
    """Test suite for get_color_gradient method."""

    @pytest.mark.parametrize(
        "coverage,expected_start,expected_end",
        [
            (85.0, "#34D058", "#28A745"),  # High coverage
            (80.0, "#34D058", "#28A745"),  # Boundary 80
            (70.0, "#A3C51C", "#8FA31C"),  # Medium-high coverage
            (60.0, "#A3C51C", "#8FA31C"),  # Boundary 60
            (50.0, "#DFB317", "#C99A00"),  # Medium coverage
            (40.0, "#DFB317", "#C99A00"),  # Boundary 40
            (30.0, "#E05D44", "#C9302C"),  # Low coverage
        ],
    )
    def test_get_color_gradient(
        self, coverage: float, expected_start: str, expected_end: str
    ) -> None:
        """Test get_color_gradient returns correct colors for coverage levels."""
        start, end = BadgeGenerator.get_color_gradient(coverage)
        assert start == expected_start
        assert end == expected_end


# pylint: disable=too-few-public-methods
class TestBadgeGeneratorColor:
    """Test suite for get_color method."""

    @pytest.mark.parametrize(
        "coverage,expected_color",
        [
            (85.0, "#4c1"),  # High coverage
            (80.0, "#4c1"),  # Boundary 80
            (70.0, "#a3c51c"),  # Medium-high coverage
            (60.0, "#a3c51c"),  # Boundary 60
            (50.0, "#dfb317"),  # Medium coverage
            (40.0, "#dfb317"),  # Boundary 40
            (30.0, "#e05d44"),  # Low coverage
        ],
    )
    def test_get_color(self, coverage: float, expected_color: str) -> None:
        """Test get_color returns correct color for coverage levels."""
        color = BadgeGenerator.get_color(coverage)
        assert color == expected_color


class TestBadgeGeneratorGenerateSvg:
    """Test suite for generate_svg method."""

    def test_generate_svg_valid_coverage(self) -> None:
        """Test generate_svg with valid coverage."""
        generator = BadgeGenerator()
        svg = generator.generate_svg(85.0, "coverage")
        assert isinstance(svg, str)
        assert "coverage" in svg
        assert "85.0%" in svg
        assert "svg" in svg.lower()
        assert "linearGradient" in svg

    def test_generate_svg_custom_label(self) -> None:
        """Test generate_svg with custom label."""
        generator = BadgeGenerator()
        svg = generator.generate_svg(75.0, "tests")
        assert "tests" in svg
        assert "75.0%" in svg

    @pytest.mark.parametrize(
        "coverage,expected_percentage,expected_color",
        [
            (0.0, "0.0%", "E05D44"),  # Zero coverage - red
            (100.0, "100.0%", "34D058"),  # 100% coverage - green
            (87.5, "87.5%", "34D058"),  # Decimal coverage
        ],
    )
    def test_generate_svg_coverage_values(
        self, coverage: float, expected_percentage: str, expected_color: str
    ) -> None:
        """Test generate_svg with different coverage values."""
        generator = BadgeGenerator()
        svg = generator.generate_svg(coverage)
        assert expected_percentage in svg
        assert expected_color in svg

    @pytest.mark.parametrize(
        "invalid_coverage",
        [-1.0, 101.0],
    )
    def test_generate_svg_invalid_coverage(self, invalid_coverage: float) -> None:
        """Test generate_svg raises ValueError for invalid coverage."""
        generator = BadgeGenerator()
        with pytest.raises(ValueError, match="Coverage must be between 0 and 100"):
            generator.generate_svg(invalid_coverage)

    def test_generate_svg_contains_gradient_definitions(self) -> None:
        """Test generate_svg includes gradient definitions."""
        generator = BadgeGenerator()
        svg = generator.generate_svg(85.0)
        assert 'id="label-fill"' in svg
        assert 'id="message-fill"' in svg
        assert "linearGradient" in svg

    def test_generate_svg_contains_paths(self) -> None:
        """Test generate_svg includes path elements."""
        generator = BadgeGenerator()
        svg = generator.generate_svg(85.0)
        assert 'id="label-bg"' in svg
        assert 'id="message-bg"' in svg

    def test_generate_svg_contains_text_elements(self) -> None:
        """Test generate_svg includes text elements with shadow."""
        generator = BadgeGenerator()
        svg = generator.generate_svg(85.0)
        assert 'fill="#010101"' in svg
        assert 'fill-opacity=".3"' in svg
        assert 'fill="#FFFFFF"' in svg


class TestBadgeGeneratorGenerateAndSaveBadge:
    """Test suite for generate_and_save_badge method."""

    def test_generate_and_save_badge_creates_file(self, tmp_path: Path) -> None:
        """Test generate_and_save_badge creates a file."""
        generator = BadgeGenerator()
        output_path = tmp_path / "test_badge.svg"
        generator.generate_and_save_badge(85.0, output_path, "coverage")
        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "coverage" in content
        assert "85.0%" in content

    def test_generate_and_save_badge_creates_directory(self, tmp_path: Path) -> None:
        """Test generate_and_save_badge creates parent directory if it doesn't exist."""
        generator = BadgeGenerator()
        output_path = tmp_path / "subdir" / "test_badge.svg"
        generator.generate_and_save_badge(75.0, output_path, "tests")
        assert output_path.exists()
        assert output_path.parent.exists()

    def test_generate_and_save_badge_custom_label(self, tmp_path: Path) -> None:
        """Test generate_and_save_badge with custom label."""
        generator = BadgeGenerator()
        output_path = tmp_path / "custom_badge.svg"
        generator.generate_and_save_badge(90.0, output_path, "custom")
        content = output_path.read_text(encoding="utf-8")
        assert "custom" in content
        assert "90.0%" in content

    def test_generate_and_save_badge_returns_path(self, tmp_path: Path) -> None:
        """Test generate_and_save_badge returns the output path."""
        generator = BadgeGenerator()
        output_path = tmp_path / "test_badge.svg"
        result = generator.generate_and_save_badge(85.0, output_path)
        assert result == output_path
        assert result.exists()
