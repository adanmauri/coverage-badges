"""Tests for the publish-badge.sh script.

Each test runs the script against a real git repository whose origin is a
local bare repository, the same way it runs inside a GitHub Actions checkout.
"""

import os
import subprocess  # nosec B404
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "publish-badge.sh"

# Isolate the tests from the developer's git configuration (signing, hooks, etc.).
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def git(repo: Path, *args: str) -> str:
    """Run a git command in a repository and return its stripped output."""
    result = subprocess.run(  # nosec B603 B607
        ["git", *args], cwd=repo, env=GIT_ENV, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def publish(repo: Path, badge: Path, branch: str, path: str = "coverage.svg") -> str:
    """Run the publish script and return its status output."""
    result = subprocess.run(  # nosec B603
        [str(SCRIPT), str(badge), branch, path, f"Update badge on {branch}"],
        cwd=repo,
        env=GIT_ENV,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


@pytest.fixture(name="repo")
def fixture_repo(tmp_path: Path) -> Path:
    """Create a clone with one commit on main and a bare origin."""
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    git(tmp_path, "init", "--quiet", "--bare", "--initial-branch=main", str(origin))
    git(tmp_path, "clone", "--quiet", str(origin), str(clone))
    (clone / "README.md").write_text("# Project\n", encoding="utf-8")
    git(clone, "add", "README.md")
    git(clone, "commit", "--quiet", "-m", "Initial commit")
    git(clone, "push", "--quiet", "origin", "HEAD:refs/heads/main")
    return clone


@pytest.fixture(name="badge")
def fixture_badge(tmp_path: Path) -> Path:
    """Create a badge file outside the repository."""
    badge = tmp_path / "badge.svg"
    badge.write_text("<svg>75.0%</svg>", encoding="utf-8")
    return badge


class TestPublishBadge:
    """Test suite for publish-badge.sh."""

    def test_creates_orphan_branch(self, repo: Path, badge: Path) -> None:
        """Test the first publish creates an orphan branch with only the badge."""
        assert publish(repo, badge, "badges") == "pushed"

        git(repo, "fetch", "--quiet", "origin", "badges")
        assert git(repo, "ls-tree", "--name-only", "FETCH_HEAD") == "coverage.svg"
        assert git(repo, "show", "FETCH_HEAD:coverage.svg") == "<svg>75.0%</svg>"
        assert git(repo, "rev-list", "--count", "FETCH_HEAD") == "1"

    def test_skips_unchanged_badge(self, repo: Path, badge: Path) -> None:
        """Test publishing the same badge again does not create a commit."""
        publish(repo, badge, "badges")

        assert publish(repo, badge, "badges") == "unchanged"

        git(repo, "fetch", "--quiet", "origin", "badges")
        assert git(repo, "rev-list", "--count", "FETCH_HEAD") == "1"

    def test_updates_existing_branch(self, repo: Path, badge: Path) -> None:
        """Test a changed badge is committed on top of the previous one."""
        publish(repo, badge, "badges")
        badge.write_text("<svg>80.0%</svg>", encoding="utf-8")

        assert publish(repo, badge, "badges") == "pushed"

        git(repo, "fetch", "--quiet", "origin", "badges")
        assert git(repo, "show", "FETCH_HEAD:coverage.svg") == "<svg>80.0%</svg>"
        assert git(repo, "rev-list", "--count", "FETCH_HEAD") == "2"

    def test_commits_to_existing_branch_keeping_files(self, repo: Path, badge: Path) -> None:
        """Test commit mode adds the badge to main without touching other files."""
        main_before = git(repo, "rev-parse", "HEAD")

        assert publish(repo, badge, "main", ".github/badges/coverage.svg") == "pushed"

        git(repo, "fetch", "--quiet", "origin", "main")
        files = git(repo, "ls-tree", "-r", "--name-only", "FETCH_HEAD").splitlines()
        assert files == [".github/badges/coverage.svg", "README.md"]
        assert git(repo, "rev-parse", "FETCH_HEAD^") == main_before

    def test_leaves_checkout_untouched(self, repo: Path, badge: Path) -> None:
        """Test the caller's working tree, index and HEAD are not modified."""
        (repo / "local.txt").write_text("uncommitted", encoding="utf-8")
        head_before = git(repo, "rev-parse", "HEAD")

        publish(repo, badge, "main")

        assert git(repo, "rev-parse", "HEAD") == head_before
        assert git(repo, "status", "--porcelain") == "?? local.txt"
        assert not (repo / "coverage.svg").exists()
