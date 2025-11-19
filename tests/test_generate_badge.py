"""Tests for generate_badge script."""

import logging
import sys
from pathlib import Path

import pytest

from src.generate_badge import main


class TestGenerateBadge:
    """Test suite for generate_badge script."""

    def test_main_with_output_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main function with custom output file."""
        output_file = tmp_path / "custom-badge.svg"
        monkeypatch.setattr(
            sys,
            "argv",
            ["generate_badge", "85.5", "-o", str(output_file), "-d", str(tmp_path)],
        )

        main()

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "85.5%" in content
        assert "Coverage" in content

    def test_main_with_label(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main function with custom label."""
        output_file = tmp_path / "test-badge.svg"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "generate_badge",
                "90.0",
                "-o",
                str(output_file),
                "-l",
                "tests",
                "-d",
                str(tmp_path),
            ],
        )

        main()

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "90.0%" in content
        assert "tests" in content

    def test_main_without_output_creates_default_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test main function creates default filename based on coverage."""
        monkeypatch.setattr(sys, "argv", ["generate_badge", "75", "-d", str(tmp_path)])

        main()

        expected_file = tmp_path / "coverage-75.svg"
        assert expected_file.exists()
        content = expected_file.read_text(encoding="utf-8")
        assert "75.0%" in content

    def test_main_creates_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main function creates directory if it doesn't exist."""
        output_dir = tmp_path / "new_dir"
        output_file = output_dir / "badge.svg"
        monkeypatch.setattr(
            sys,
            "argv",
            ["generate_badge", "80", "-o", "badge.svg", "-d", str(output_dir)],
        )

        main()

        assert output_dir.exists()
        assert output_file.exists()

    def test_main_logs_output(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test main function logs output message."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["generate_badge", "95", "-o", "test.svg", "-d", str(tmp_path)],
        )

        with caplog.at_level(logging.INFO):
            main()

        assert "Badge generated and saved to" in caplog.text
        assert "test.svg" in caplog.text

    def test_main_with_decimal_coverage(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test main function with decimal coverage value."""
        output_file = tmp_path / "decimal-badge.svg"
        monkeypatch.setattr(
            sys,
            "argv",
            ["generate_badge", "87.5", "-o", "decimal-badge.svg", "-d", str(tmp_path)],
        )

        main()

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "87.5%" in content
