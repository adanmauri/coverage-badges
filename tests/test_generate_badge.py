"""Tests for generate_badge script."""

import logging
from pathlib import Path

import pytest

from src.generate_badge import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestGenerateBadge:
    """Test suite for generate_badge script."""

    def test_main_with_value(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main function with a fixed coverage value."""
        output_file = tmp_path / "custom-badge.svg"

        main(["85.5", "-o", str(output_file)])

        content = output_file.read_text(encoding="utf-8")
        assert "85.5%" in content
        assert "Coverage" in content
        assert capsys.readouterr().out == "85.5\n"

    def test_main_with_report(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main function reads the value from a coverage report."""
        output_file = tmp_path / "badge.svg"

        main(["--report", str(FIXTURES / "lcov.info"), "-o", str(output_file)])

        assert "75.0%" in output_file.read_text(encoding="utf-8")
        assert capsys.readouterr().out == "75.0\n"

    def test_main_with_label(self, tmp_path: Path) -> None:
        """Test main function with custom label."""
        output_file = tmp_path / "test-badge.svg"

        main(["90.0", "-o", str(output_file), "-l", "tests"])

        assert "tests" in output_file.read_text(encoding="utf-8")

    def test_main_default_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main function writes coverage.svg by default."""
        monkeypatch.chdir(tmp_path)

        main(["75"])

        assert "75.0%" in (tmp_path / "coverage.svg").read_text(encoding="utf-8")

    def test_main_creates_directory(self, tmp_path: Path) -> None:
        """Test main function creates the output directory if it doesn't exist."""
        output_file = tmp_path / "new_dir" / "badge.svg"

        main(["80", "-o", str(output_file)])

        assert output_file.exists()

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("99.96", "99.9"),
            ("87.55", "87.5"),
            ("100", "100.0"),
            ("0", "0.0"),
        ],
    )
    def test_main_truncates_value(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str], value: str, expected: str
    ) -> None:
        """Test the value is truncated to one decimal so it is never overstated."""
        output_file = tmp_path / "badge.svg"

        main([value, "-o", str(output_file)])

        assert capsys.readouterr().out == f"{expected}\n"
        assert f"{expected}%" in output_file.read_text(encoding="utf-8")

    def test_main_logs_output(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """Test main function logs output message."""
        with caplog.at_level(logging.INFO):
            main(["95", "-o", str(tmp_path / "test.svg")])

        assert "Badge generated and saved to" in caplog.text
        assert "test.svg" in caplog.text

    @pytest.mark.parametrize(
        "argv",
        [
            [],
            ["85", "--report", "coverage.xml"],
        ],
    )
    def test_main_requires_exactly_one_source(self, argv: list[str]) -> None:
        """Test a value or a report is required, but not both."""
        with pytest.raises(SystemExit) as error:
            main(argv)
        assert error.value.code == 2

    @pytest.mark.parametrize(
        "argv,message",
        [
            (["--report", "missing.xml"], "No such file"),
            (["150"], "Coverage must be between 0 and 100"),
        ],
    )
    def test_main_reports_errors(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        argv: list[str],
        message: str,
    ) -> None:
        """Test invalid input exits with code 1 and a readable message."""
        with pytest.raises(SystemExit) as error:
            main([*argv, "-o", str(tmp_path / "badge.svg")])
        assert error.value.code == 1
        assert message in capsys.readouterr().err
