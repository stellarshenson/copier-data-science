"""End-to-end `copier update` test for switching AI assistant.

post_gen deletes the switched-away assistant's files, but copier's update runs the
tasks BEFORE applying its diff patch, and the patch restores anything it is not told to
exclude. The only thing that keeps those deletions is listing the assistant paths in
`_skip_if_exists`, which copier feeds to `git apply --exclude`.

Driving post_gen directly - as the other assistant tests do - cannot see the patch step,
so a regression there is invisible to them. This test runs a real copy-then-update
against a throwaway tagged clone of the template.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest
from conftest import COPIER_DIR, get_copier_cmd

COPY_DATA = [
    "project_name=p",
    "repo_name=r",
    "module_name=m",
    "environment_manager=uv",
    "dependency_file=pyproject.toml",
    "docs=none",
    "include_code_scaffold=Yes",
    "testing_framework=pytest",
    "env_encryption=No",
    "dataset_storage=none",
    "docker_support=No",
    "git_init=No",
]

USER_EDIT = "\n## MY OWN SECTION\n"


def _git(*args, cwd):
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _head_has_ai_assistant():
    """The committed template must already carry the ai_assistant question."""
    result = subprocess.run(
        ["git", "show", "HEAD:copier.yml"],
        cwd=COPIER_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and "ai_assistant:" in result.stdout


@pytest.mark.skipif(
    not _head_has_ai_assistant(),
    reason="needs the ai_assistant question committed (copier --vcs-ref reads git history)",
)
def test_switching_assistant_survives_a_real_update():
    copier_cmd = get_copier_cmd()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        template = tmp_path / "template"
        project = tmp_path / "project"

        # Throwaway clone of the committed template, tagged before and after a no-op
        # change so `copier update` has a newer ref to move to
        assert (
            _git("clone", "--no-local", "-q", str(COPIER_DIR), str(template), cwd=tmp).returncode
            == 0
        )
        assert _git("tag", "vA", cwd=template).returncode == 0
        (template / "template" / "README.md").write_text(
            (template / "template" / "README.md").read_text() + "\n"
        )
        assert _git("commit", "-qam", "tick", cwd=template).returncode == 0
        assert _git("tag", "vB", cwd=template).returncode == 0

        # copier only honours --vcs-ref for a git URL, not a plain directory path
        url = f"git+file://{template}"

        copy = subprocess.run(
            [copier_cmd, "copy", "--trust", "--defaults", "--vcs-ref", "vA", url, str(project)]
            + [arg for d in COPY_DATA + ["ai_assistant=gemini"] for arg in ("-d", d)],
            capture_output=True,
            text=True,
        )
        assert copy.returncode == 0, f"copier copy failed: {copy.stderr}"
        gemini_md = project / "GEMINI.md"
        assert gemini_md.is_file(), "gemini should place GEMINI.md at the project root"

        assert _git("init", "-qb", "main", cwd=project).returncode == 0
        assert _git("add", "-A", cwd=project).returncode == 0
        assert _git("commit", "-qm", "init", cwd=project).returncode == 0
        gemini_md.write_text(gemini_md.read_text() + USER_EDIT)
        assert _git("commit", "-qam", "edit", cwd=project).returncode == 0

        update = subprocess.run(
            [copier_cmd, "update", "--trust", "--defaults", "--vcs-ref", "vB"]
            + ["-d", "ai_assistant=claude"],
            cwd=project,
            capture_output=True,
            text=True,
        )
        assert update.returncode == 0, f"copier update failed: {update.stderr}"

        placed = project / ".claude" / "CLAUDE.md"
        assert placed.is_file(), "the new assistant's instructions should be in place"
        assert USER_EDIT in placed.read_text(), "the user's edits must be carried over"
        assert not gemini_md.exists(), (
            "the switched-away GEMINI.md must not be restored by the update patch"
        )
        assert not (project / ".gemini").exists(), (
            "the switched-away .gemini/ must not be restored by the update patch"
        )
