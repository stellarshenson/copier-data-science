"""Tests for git initialization option.

These tests verify that the git_init option correctly initializes a git repository
when enabled, skips initialization when disabled, and does not re-init during updates.
"""

import subprocess
import tempfile
from pathlib import Path

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

    def test_git_not_reinitialized_during_update(self):
        """Test that copier update does not re-init git when .git already exists.

        Uses git+file:// URL so copier properly checks out git refs.
        """
        copier_cmd = get_copier_cmd()
        git_url = f"git+file://{COPIER_DIR}"

        with tempfile.TemporaryDirectory() as tmp:
            project_path = Path(tmp) / "test-repo"

            # Create project with git_init=Yes
            result = subprocess.run(
                [
                    copier_cmd,
                    "copy",
                    "--trust",
                    "--defaults",
                    "--vcs-ref",
                    "HEAD",
                    "-d",
                    "git_init=Yes",
                    git_url,
                    str(project_path),
                ],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"copier copy failed: {result.stderr}"

            # Stage and commit (required for copier update)
            subprocess.run(["git", "add", "-A"], cwd=project_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial"],
                cwd=project_path,
                check=True,
            )

            # Record the original .git state (HEAD commit)
            orig_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
            ).stdout.strip()

            # Run copier update
            result = subprocess.run(
                [
                    copier_cmd,
                    "update",
                    "--trust",
                    "--defaults",
                    "--vcs-ref",
                    "HEAD",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"copier update failed: {result.stderr}"

            # Verify git repo still intact - original commit still exists
            head_after = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
            ).stdout.strip()
            assert head_after == orig_head, (
                "HEAD should be unchanged - git init should not have run during update"
            )

            # Verify "Reinitialized" does NOT appear in output
            combined = result.stdout + result.stderr
            assert "Reinitialized" not in combined, (
                "git should not be re-initialized during update"
            )
