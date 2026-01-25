"""Tests for git initialization option.

These tests verify that the git_init option correctly initializes a git repository
when enabled and skips initialization when disabled.
"""

import subprocess

from conftest import COPIER_DIR, get_copier_cmd


class TestGitInit:
    """Test git initialization option."""

    def test_git_initialized_when_enabled(self, tmp_path):
        """Test that git repository is initialized when git_init=Yes."""
        project_path = tmp_path / "test-git-yes"

        result = subprocess.run(
            [
                get_copier_cmd(),
                "copy",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "HEAD",
                "-d",
                "git_init=Yes",
                str(COPIER_DIR),
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Verify .git directory exists
        git_dir = project_path / ".git"
        assert git_dir.exists(), ".git directory should exist when git_init=Yes"
        assert git_dir.is_dir(), ".git should be a directory"

        # Verify it's a valid git repo with main branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "git branch command should succeed"
        assert result.stdout.strip() == "main", "Default branch should be 'main'"

    def test_git_not_initialized_when_disabled(self, tmp_path):
        """Test that git repository is NOT initialized when git_init=No."""
        project_path = tmp_path / "test-git-no"

        result = subprocess.run(
            [
                get_copier_cmd(),
                "copy",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "HEAD",
                "-d",
                "git_init=No",
                str(COPIER_DIR),
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Verify .git directory does NOT exist
        git_dir = project_path / ".git"
        assert not git_dir.exists(), ".git directory should NOT exist when git_init=No"

    def test_git_init_defaults_to_yes(self, tmp_path):
        """Test that git_init defaults to Yes (git is initialized by default)."""
        project_path = tmp_path / "test-git-default"

        # Don't pass git_init - should use default (Yes)
        result = subprocess.run(
            [
                get_copier_cmd(),
                "copy",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "HEAD",
                str(COPIER_DIR),
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Verify .git directory exists (default is Yes)
        git_dir = project_path / ".git"
        assert git_dir.exists(), (
            ".git directory should exist by default (git_init defaults to Yes)"
        )
