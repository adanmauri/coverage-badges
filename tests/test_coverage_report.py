"""Tests for coverage report parsing."""

from pathlib import Path

import pytest

from src.coverage_report import detect_format, read_coverage

FIXTURES = Path(__file__).parent / "fixtures"

# Every fixture describes the same project: 6 of 8 lines covered.
REPORTS = [
    ("cobertura.xml", "cobertura"),
    ("jacoco.xml", "jacoco"),
    ("lcov.info", "lcov"),
    ("coverage.out", "go"),
    ("coverage.json", "coverage-py"),
    ("coverage-summary.json", "istanbul"),
]


class TestReadCoverage:
    """Test suite for read_coverage."""

    @pytest.mark.parametrize("file_name,report_format", REPORTS)
    def test_explicit_format(self, file_name: str, report_format: str) -> None:
        """Test each parser reads the total from its fixture."""
        assert read_coverage(FIXTURES / file_name, report_format) == pytest.approx(75.0)

    @pytest.mark.parametrize("file_name,report_format", REPORTS)
    def test_auto_detects_format(self, file_name: str, report_format: str) -> None:
        """Test format detection matches the fixture format."""
        content = (FIXTURES / file_name).read_text(encoding="utf-8")
        assert detect_format(content) == report_format
        assert read_coverage(FIXTURES / file_name) == pytest.approx(75.0)

    def test_unknown_format(self) -> None:
        """Test an unknown format name is rejected."""
        with pytest.raises(ValueError, match="Unknown report format"):
            read_coverage(FIXTURES / "lcov.info", "clover")

    def test_missing_file(self, tmp_path: Path) -> None:
        """Test a missing report raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_coverage(tmp_path / "missing.xml")


class TestInvalidReports:
    """Test suite for invalid or unsupported report content."""

    @pytest.mark.parametrize(
        "content",
        [
            "plain text",
            "<html></html>",
            '{"files": {}}',
        ],
    )
    def test_undetectable_content(self, tmp_path: Path, content: str) -> None:
        """Test content that matches no format asks for an explicit format."""
        report = tmp_path / "report"
        report.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match="Could not detect"):
            read_coverage(report)

    @pytest.mark.parametrize(
        "report_format,content,message",
        [
            ("cobertura", "<coverage", "Invalid XML"),
            ("cobertura", "<coverage/>", "missing <coverage line-rate>"),
            ("jacoco", "<coverage/>", "missing <report> root"),
            ("jacoco", '<report><counter type="METHOD"/></report>', "missing report-level"),
            ("jacoco", '<report><counter type="LINE"/></report>', "any coverable lines"),
            ("lcov", "TN:\nend_of_record\n", "any coverable lines"),
            ("go", "mode: set\nnot-a-block\n", "Invalid Go coverprofile line"),
            ("go", "mode: set\n", "any coverable lines"),
            ("coverage-py", "[]", "expected an object"),
            ("coverage-py", "{", "Invalid JSON"),
            ("coverage-py", '{"totals": {}}', "missing totals.percent_covered"),
            ("istanbul", '{"total": {"lines": {}}}', "missing total.lines"),
        ],
    )
    def test_invalid_content(
        self, tmp_path: Path, report_format: str, content: str, message: str
    ) -> None:
        """Test each parser rejects malformed content with a clear message."""
        report = tmp_path / "report"
        report.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            read_coverage(report, report_format)
