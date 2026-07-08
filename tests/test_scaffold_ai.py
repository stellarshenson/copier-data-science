"""Tests for the ai/ scaffolding option.

These tests verify that the ai/ folder (with a single .gitkeep) is scaffolded when
scaffold_ai=Yes, absent when scaffold_ai=No, and that it defaults to No.
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


class TestScaffoldAi:
    """Test ai/ scaffolding option."""

    def test_ai_created_when_enabled(self, tmp_path):
        project_path = tmp_path / "test-ai-yes"
        result = _copy(project_path, "scaffold_ai=Yes", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        ai_dir = project_path / "ai"
        assert ai_dir.is_dir(), "ai/ should exist when scaffold_ai=Yes"
        assert (ai_dir / ".gitkeep").exists(), "ai/.gitkeep should exist"
        # Only the .gitkeep - internal structure is framework-dependent
        contents = [p.name for p in ai_dir.iterdir()]
        assert contents == [".gitkeep"], f"ai/ should contain only .gitkeep, got {contents}"

    def test_ai_absent_when_disabled(self, tmp_path):
        project_path = tmp_path / "test-ai-no"
        result = _copy(project_path, "scaffold_ai=No", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "ai").exists(), "ai/ should NOT exist when scaffold_ai=No"

    def test_ai_defaults_to_no(self, tmp_path):
        project_path = tmp_path / "test-ai-default"
        result = _copy(project_path, "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "ai").exists(), "ai/ should default to absent (scaffold_ai=No)"
