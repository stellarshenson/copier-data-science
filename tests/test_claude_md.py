"""Tests for the CLAUDE.md scaffolding option.

These tests verify that CLAUDE.md is scaffolded when claude_md=Yes, absent when
claude_md=No, and that it defaults to No.
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


class TestClaudeMd:
    """Test CLAUDE.md scaffolding option."""

    def test_claude_md_created_when_enabled(self, tmp_path):
        project_path = tmp_path / "test-claude-yes"
        result = _copy(project_path, "claude_md=Yes", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        claude_md = project_path / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md should exist when claude_md=Yes"

        content = claude_md.read_text()
        # No unrendered Jinja left behind
        assert "{{" not in content and "{%" not in content
        # Key sections present
        assert "make help" in content
        assert "Make Commands" in content

    def test_claude_md_absent_when_disabled(self, tmp_path):
        project_path = tmp_path / "test-claude-no"
        result = _copy(project_path, "claude_md=No", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "CLAUDE.md").exists(), (
            "CLAUDE.md should NOT exist when claude_md=No"
        )

    def test_claude_md_defaults_to_no(self, tmp_path):
        project_path = tmp_path / "test-claude-default"
        result = _copy(project_path, "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "CLAUDE.md").exists(), (
            "CLAUDE.md should default to absent (claude_md=No)"
        )
