"""Tests for the agents/ scaffolding option.

The agents/ folder holds deployable agentic resources (workflows, exported skills), as
opposed to the assistant's project-internal dot-folder. These tests verify that agents/
(with a single .gitkeep) is scaffolded when scaffold_agents=Yes, absent when
scaffold_agents=No, and that it defaults to No.
"""

import subprocess

from conftest import COPIER_DIR, get_copier_cmd, run_post_gen


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


class TestScaffoldAgents:
    """Test agents/ scaffolding option."""

    def test_agents_created_when_enabled(self, tmp_path):
        project_path = tmp_path / "test-agents-yes"
        result = _copy(project_path, "scaffold_agents=Yes", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        agents_dir = project_path / "agents"
        assert agents_dir.is_dir(), "agents/ should exist when scaffold_agents=Yes"
        assert (agents_dir / ".gitkeep").exists(), "agents/.gitkeep should exist"
        # Only the .gitkeep - internal structure is framework-dependent
        contents = [p.name for p in agents_dir.iterdir()]
        assert contents == [".gitkeep"], f"agents/ should contain only .gitkeep, got {contents}"

    def test_agents_absent_when_disabled(self, tmp_path):
        project_path = tmp_path / "test-agents-no"
        result = _copy(project_path, "scaffold_agents=No", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "agents").exists(), (
            "agents/ should NOT exist when scaffold_agents=No"
        )

    def test_agents_defaults_to_no(self, tmp_path):
        project_path = tmp_path / "test-agents-default"
        result = _copy(project_path, "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "agents").exists(), (
            "agents/ should default to absent (scaffold_agents=No)"
        )

    def test_agents_independent_of_ai_assistant(self, tmp_path):
        """agents/ is a deliverable; the dot-folder is internal. They are independent."""
        project_path = tmp_path / "test-agents-with-claude"
        result = _copy(project_path, "scaffold_agents=Yes", "ai_assistant=claude", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert (project_path / "agents" / ".gitkeep").exists(), "agents/ should exist"
        assert (project_path / ".claude" / "CLAUDE.md").is_file(), (
            ".claude/CLAUDE.md should exist alongside agents/"
        )


class TestAgentsDeleteGuard:
    """agents/ is only removed when the template owns it.

    Regression pin: scaffold_agents defaults to No, so an unguarded delete wiped a user's
    agents/ tree on every update - including for older projects that never answered the
    question. Only a folder holding nothing but our own .gitkeep may be removed.
    """

    def test_user_content_survives_scaffold_agents_no(self, tmp_path):
        project_path = tmp_path / "proj"
        (project_path / "agents" / "workflows").mkdir(parents=True)
        payload = project_path / "agents" / "workflows" / "deploy.yaml"
        payload.write_text("deploy: yes\n")

        result = run_post_gen(project_path, "--scaffold-agents", "No")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        assert payload.exists(), "user content in agents/ must survive scaffold_agents=No"

    def test_template_owned_agents_removed(self, tmp_path):
        project_path = tmp_path / "proj"
        (project_path / "agents").mkdir(parents=True)
        (project_path / "agents" / ".gitkeep").write_text("")

        result = run_post_gen(project_path, "--scaffold-agents", "No")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        assert not (project_path / "agents").exists(), (
            "a gitkeep-only agents/ is template-owned and should be removed"
        )
