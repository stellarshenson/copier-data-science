"""Tests for the GitHub Actions workflow option.

These tests verify that .github/workflows/tests.yml is scaffolded when
github_actions=Yes, absent when github_actions=No, and that it defaults to No.
"""

import subprocess

from conftest import COPIER_DIR, get_copier_cmd


def _copy(project_path, *data):
    args = [
        get_copier_cmd(),
        "copy",
        "--trust",
        "--defaults",
        "--vcs-ref",
        "HEAD",
    ]
    for d in data:
        args += ["-d", d]
    args += [str(COPIER_DIR), str(project_path)]
    return subprocess.run(args, capture_output=True, text=True)


class TestGithubActions:
    """Test GitHub Actions workflow option."""

    def test_workflow_created_when_enabled(self, tmp_path):
        project_path = tmp_path / "test-gha-yes"
        result = _copy(project_path, "github_actions=Yes", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        workflow = project_path / ".github" / "workflows" / "tests.yml"
        assert workflow.exists(), "workflow should exist when github_actions=Yes"

        content = workflow.read_text()
        # No unrendered Jinja left behind
        assert "{{" not in content and "{%" not in content
        # Runs the make targets
        assert "make install" in content
        assert "make lint" in content
        assert "make test" in content

    def test_workflow_absent_when_disabled(self, tmp_path):
        project_path = tmp_path / "test-gha-no"
        result = _copy(project_path, "github_actions=No", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / ".github").exists(), (
            ".github should NOT exist when github_actions=No"
        )

    def test_workflow_defaults_to_no(self, tmp_path):
        project_path = tmp_path / "test-gha-default"
        result = _copy(project_path, "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / ".github").exists(), (
            ".github should default to absent (github_actions=No)"
        )
