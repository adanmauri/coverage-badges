"""Tests for generate_all_badges script."""

import logging
from pathlib import Path

import pytest

from src.generate_all_badges import main


class TestGenerateAllBadges:
    """Test suite for generate_all_badges script."""

    def test_main_generates_all_badges(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test main function generates badges for all coverage levels."""
        # Change to tmp_path directory
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)

        try:
            main()

            # Check that badges directory was created
            badges_dir = tmp_path / "badges"
            assert badges_dir.exists()

            # Check badges for 0% to 100% in 5% increments
            for coverage in range(0, 101, 5):
                badge_file = badges_dir / f"coverage-{coverage}.svg"
                assert badge_file.exists(), f"Badge for {coverage}% should exist"
                content = badge_file.read_text(encoding="utf-8")
                assert f"{coverage}.0%" in content

        finally:
            monkeypatch.chdir(original_cwd)

    def test_main_creates_badges_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test main function creates badges directory if it doesn't exist."""
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)

        try:
            badges_dir = tmp_path / "badges"
            assert not badges_dir.exists()

            main()

            assert badges_dir.exists()

        finally:
            monkeypatch.chdir(original_cwd)

    def test_main_logs_output(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test main function logs output messages."""
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)

        try:
            with caplog.at_level(logging.INFO):
                main()

            assert "Badge generated and saved to" in caplog.text
            assert "badges" in caplog.text

        finally:
            monkeypatch.chdir(original_cwd)

    def test_main_badge_content_is_valid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that generated badges contain valid SVG content."""
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)

        try:
            main()

            badges_dir = tmp_path / "badges"
            # Check a few badges for valid SVG structure
            for coverage in [0, 50, 100]:
                badge_file = badges_dir / f"coverage-{coverage}.svg"
                content = badge_file.read_text(encoding="utf-8")
                assert content.startswith("<svg")
                assert content.endswith("</svg>")
                assert "xmlns" in content
                assert f"{coverage}.0%" in content

        finally:
            monkeypatch.chdir(original_cwd)
