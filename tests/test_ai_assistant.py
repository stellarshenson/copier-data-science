"""Tests for the ai_assistant option.

Each assistant reads its project instructions from a different path, so the template
places the file where that tool actually looks for it and creates a dot-folder for the
assistant's project-internal resources:

    claude  -> .claude/CLAUDE.md
    codex   -> AGENTS.md + .codex/
    gemini  -> GEMINI.md + .gemini/
    generic -> AGENTS.md + .agents/

These tests verify each layout, that nothing is scaffolded for the default (none), and
that the instructions file renders without leftover Jinja.
"""

import subprocess

import pytest
from conftest import COPIER_DIR, POST_GEN_MATCHING_DATA, get_copier_cmd, run_post_gen

# assistant -> (instructions file, internal folder)
LAYOUTS = {
    "claude": (".claude/CLAUDE.md", ".claude"),
    "codex": ("AGENTS.md", ".codex"),
    "gemini": ("GEMINI.md", ".gemini"),
    "generic": ("AGENTS.md", ".agents"),
}

# Files and folders that must not be left behind for a non-matching assistant
ALL_INSTRUCTION_FILES = ["CLAUDE.md", "AGENTS.md", "GEMINI.md"]
ALL_INTERNAL_DIRS = [".claude", ".codex", ".gemini", ".agents"]


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


class TestAiAssistant:
    """Test the ai_assistant scaffolding option."""

    @pytest.mark.parametrize("assistant", sorted(LAYOUTS))
    def test_instructions_placed_where_tool_reads_them(self, assistant, tmp_path):
        instructions, internal_dir = LAYOUTS[assistant]
        project_path = tmp_path / f"test-{assistant}"
        result = _copy(project_path, f"ai_assistant={assistant}", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        placed = project_path / instructions
        assert placed.is_file(), f"{instructions} should exist for ai_assistant={assistant}"
        assert (project_path / internal_dir).is_dir(), (
            f"{internal_dir}/ should exist for ai_assistant={assistant}"
        )

        content = placed.read_text()
        # No unrendered Jinja left behind
        assert "{{" not in content and "{%" not in content
        # Key sections present
        assert "make help" in content
        assert "Make Commands" in content

    @pytest.mark.parametrize("assistant", sorted(LAYOUTS))
    def test_other_assistants_not_scaffolded(self, assistant, tmp_path):
        instructions, internal_dir = LAYOUTS[assistant]
        project_path = tmp_path / f"test-{assistant}-exclusive"
        result = _copy(project_path, f"ai_assistant={assistant}", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Only the chosen assistant's folder exists
        for candidate in ALL_INTERNAL_DIRS:
            if candidate == internal_dir:
                continue
            assert not (project_path / candidate).exists(), (
                f"{candidate}/ should not exist for ai_assistant={assistant}"
            )

        # No stray instructions file at the root (the template ships CLAUDE.md there)
        for candidate in ALL_INSTRUCTION_FILES:
            if candidate == instructions:
                continue
            assert not (project_path / candidate).exists(), (
                f"{candidate} should not exist at the root for ai_assistant={assistant}"
            )

    def test_nothing_scaffolded_when_none(self, tmp_path):
        project_path = tmp_path / "test-assistant-none"
        result = _copy(project_path, "ai_assistant=none", "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        for candidate in ALL_INSTRUCTION_FILES:
            assert not (project_path / candidate).exists(), (
                f"{candidate} should NOT exist when ai_assistant=none"
            )
        for candidate in ALL_INTERNAL_DIRS:
            assert not (project_path / candidate).exists(), (
                f"{candidate}/ should NOT exist when ai_assistant=none"
            )

    def test_defaults_to_none(self, tmp_path):
        project_path = tmp_path / "test-assistant-default"
        result = _copy(project_path, "git_init=No")
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        assert not (project_path / "CLAUDE.md").exists(), (
            "CLAUDE.md should default to absent (ai_assistant=none)"
        )
        assert not (project_path / ".claude").exists(), (
            ".claude/ should default to absent (ai_assistant=none)"
        )


class TestAiAssistantUpdate:
    """Update scenarios, which `copier copy` alone cannot reach.

    Regression pins for two shipped defects: selecting `none` on an update deleted an
    instructions file the user had edited, and switching assistant rendered the new file
    from a pristine template, stranding the user's edits in the old one. Both rest on
    telling untouched template output apart from an edited file - a comparison that was
    silently never true until `keep_trailing_newline` was set, so the second test here
    fails the moment that comparison goes dead again.
    """

    EDIT = "\n## MY OWN SECTION\n"

    def test_edited_instructions_survive_switch_to_none(self, tmp_path):
        project_path = tmp_path / "edited-none"
        assert (
            _copy(
                project_path, "ai_assistant=claude", "git_init=No", *POST_GEN_MATCHING_DATA
            ).returncode
            == 0
        )

        instructions = project_path / ".claude" / "CLAUDE.md"
        instructions.write_text(instructions.read_text() + self.EDIT)

        result = run_post_gen(project_path, "--ai-assistant", "none")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        assert instructions.exists(), "an edited instructions file must never be deleted"
        assert self.EDIT in instructions.read_text()

    def test_untouched_instructions_removed_on_switch_to_none(self, tmp_path):
        project_path = tmp_path / "untouched-none"
        assert (
            _copy(
                project_path, "ai_assistant=codex", "git_init=No", *POST_GEN_MATCHING_DATA
            ).returncode
            == 0
        )
        assert (project_path / "AGENTS.md").is_file()

        result = run_post_gen(project_path, "--ai-assistant", "none")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        assert not (project_path / "AGENTS.md").exists(), (
            "an untouched template copy should be removed when switching to none"
        )

    def test_switching_assistant_carries_edits_and_clears_the_old_file(self, tmp_path):
        project_path = tmp_path / "codex-to-gemini"
        assert (
            _copy(
                project_path, "ai_assistant=codex", "git_init=No", *POST_GEN_MATCHING_DATA
            ).returncode
            == 0
        )

        old = project_path / "AGENTS.md"
        old.write_text(old.read_text() + self.EDIT)

        result = run_post_gen(project_path, "--ai-assistant", "gemini")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        new = project_path / "GEMINI.md"
        assert new.is_file(), "the new assistant's instructions file should be created"
        assert self.EDIT in new.read_text(), "the user's edits must be carried over"
        assert not old.exists(), "the switched-away file must not keep being read"
        assert not (project_path / ".codex").exists(), "the old dot-folder should be gone"


class TestAiAssistantCopyPath:
    """The copy path, which is NOT always an empty directory.

    `copier copy --overwrite` and `copier recopy` both report the operation as "copy"
    while running over a directory that already holds the user's files, so nothing on
    this path may delete or consume an instructions file on the strength of the
    operation alone - only a content check may.
    """

    HAND_WRITTEN = "# my own notes for another tool\n"

    def test_copy_keeps_a_hand_written_instructions_file(self, tmp_path):
        project_path = tmp_path / "recopy-none"
        project_path.mkdir()
        existing = project_path / "CLAUDE.md"
        existing.write_text(self.HAND_WRITTEN)

        result = run_post_gen(project_path, "--ai-assistant", "none", operation="copy")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        assert existing.exists(), "a hand-written CLAUDE.md must survive a copy/recopy"
        assert existing.read_text() == self.HAND_WRITTEN

    def test_copy_does_not_consume_another_tools_file(self, tmp_path):
        project_path = tmp_path / "recopy-claude"
        project_path.mkdir()
        other = project_path / "AGENTS.md"
        other.write_text(self.HAND_WRITTEN)

        result = run_post_gen(project_path, "--ai-assistant", "claude", operation="copy")
        assert result.returncode == 0, f"post_gen failed: {result.stderr}"

        assert other.exists(), "a copy has no previous answer to switch from"
        assert other.read_text() == self.HAND_WRITTEN
        assert (project_path / ".claude" / "CLAUDE.md").is_file(), (
            "the template's own instructions should still be delivered"
        )
