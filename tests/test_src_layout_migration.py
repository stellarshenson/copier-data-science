"""
Tests for src layout migration (v1.2.x flat -> v1.3.x src).

Tests that:
1. Fresh copies produce src layout with no lib_ prefix
2. config.py uses correct parents depth for src layout
3. pyproject.toml has src layout setuptools config
4. copier update from v1.2.16 migrates flat layout to src layout (requires commit)
"""

import subprocess
import tempfile
from pathlib import Path

import pytest
from conftest import COPIER_DIR, bake_project, config_generator, get_copier_cmd

GITHUB_TEMPLATE_URL = "https://github.com/stellarshenson/copier-data-science.git"
# git+file:// prefix is required for copier to properly checkout git refs from local repos
# Without it, copier treats local paths as plain directories and ignores --vcs-ref
GIT_LOCAL_URL = f"git+file://{COPIER_DIR}"


def test_fresh_copy_has_src_layout():
    """Verify fresh copy at HEAD creates src layout."""
    config = next(config_generator(fast=1))
    with bake_project(config) as project_dir:
        # Module should be under src/
        src_module = project_dir / "src" / config["module_name"]
        assert src_module.is_dir(), f"src/{config['module_name']}/ should exist"
        assert (src_module / "__init__.py").exists(), "src module should have __init__.py"

        # Old flat layout should NOT exist
        flat_module = project_dir / config["module_name"]
        assert not flat_module.exists(), f"{config['module_name']}/ should not exist at root"


def test_fresh_copy_config_parents_depth():
    """Verify config.py uses parents[2] for src layout root detection."""
    config = next(config_generator(fast=1))
    # Ensure we get code scaffold for config.py
    config["include_code_scaffold"] = "Yes"
    with bake_project(config) as project_dir:
        config_py = project_dir / "src" / config["module_name"] / "config.py"
        assert config_py.exists(), "config.py should exist in src layout"
        content = config_py.read_text()
        assert "parents[2]" in content, "config.py should use parents[2] for src layout"
        assert "parents[1]" not in content, "config.py should NOT use parents[1]"


def test_fresh_copy_pyproject_src_layout():
    """Verify pyproject.toml has src layout setuptools config."""
    config = next(config_generator(fast=1))
    with bake_project(config) as project_dir:
        pyproject = (project_dir / "pyproject.toml").read_text()
        assert 'where = ["src"]' in pyproject, "setuptools should look in src/"


def test_fresh_copy_no_lib_prefix():
    """Verify default module_name no longer has lib_ prefix."""
    config = next(config_generator(fast=1))
    # Default module_name should NOT start with lib_
    assert not config["module_name"].startswith("lib_"), (
        f"Default module_name should not have lib_ prefix, got: {config['module_name']}"
    )


def _is_src_layout_committed():
    """Check if current HEAD has the src layout changes committed."""
    result = subprocess.run(
        ["git", "ls-tree", "--name-only", "HEAD", "template/src/"],
        cwd=COPIER_DIR,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and "template/src/" in result.stdout


@pytest.mark.skipif(
    not _is_src_layout_committed(),
    reason="Migration test requires src layout changes to be committed (copier --vcs-ref needs committed state)",
)
def test_flat_to_src_migration():
    """Test migration from v1.2.16 (flat layout) to HEAD (src layout).

    Uses local repo: create project at v1.2.16 tag, then copier update
    to HEAD. Verifies user code is preserved and moved to src/.

    Requires src layout changes to be committed - copier --vcs-ref reads from
    git history, not the working tree.
    """
    copier_cmd = get_copier_cmd()

    with tempfile.TemporaryDirectory() as tmp:
        project_path = Path(tmp) / "my-test-repo"

        # Step 1: Create project from local repo at v1.2.16 (flat layout)
        # Use git+file:// URL so copier properly checks out the git ref
        result = subprocess.run(
            [
                copier_cmd,
                "copy",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "v1.2.16",
                GIT_LOCAL_URL,
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Step 2: Verify flat layout was created (v1.2.16 behavior)
        # Default module_name at v1.2.16 is lib_<repo_name>
        module_name = "lib_my_test_repo"
        flat_module = project_path / module_name
        assert flat_module.is_dir(), f"{module_name}/ should exist in v1.2.16 flat layout"
        assert not (project_path / "src").exists(), "src/ should not exist in v1.2.16"

        # Step 3: Add custom user code to simulate real modifications
        custom_file = flat_module / "custom_analysis.py"
        custom_file.write_text(
            '"""Custom user analysis module."""\n\n'
            'CUSTOM_MARKER = "user_code_preserved"\n'
            "CUSTOM_VALUE = 42\n"
        )

        # Also modify an existing file to verify user changes are kept
        config_py = flat_module / "config.py"
        if config_py.exists():
            original_config = config_py.read_text()
            config_py.write_text(
                original_config + "\n# User's custom config addition\nMY_VAR = 'test'\n"
            )

        # Step 4: Git init + commit (required for copier update)
        subprocess.run(["git", "init", "-b", "main"], cwd=project_path, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_path, check=True)
        subprocess.run(["git", "add", "-A"], cwd=project_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial project from v1.2.16"],
            cwd=project_path,
            check=True,
        )

        # Step 5: copier update to HEAD (v1.3.x src layout)
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
        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        assert result.returncode == 0, f"copier update failed: {result.stderr}"

        # Step 6: Verify migration results

        # New src layout should exist with all files
        src_module = project_path / "src" / module_name
        assert src_module.is_dir(), f"src/{module_name}/ should exist after migration"

        # User's custom code should be in src/ location
        migrated_custom = src_module / "custom_analysis.py"
        assert migrated_custom.exists(), "User's custom_analysis.py should be in src/"
        content = migrated_custom.read_text()
        assert "user_code_preserved" in content, "Custom marker should be in migrated file"
        assert "CUSTOM_VALUE = 42" in content, "Custom value should be in migrated file"

        # User's modifications to config.py should be preserved in src/
        migrated_config = src_module / "config.py"
        assert migrated_config.exists(), "config.py should exist in src layout"
        config_content = migrated_config.read_text()
        assert "MY_VAR" in config_content, "User's config.py modifications should be preserved"

        # config.py should have parents[2] (not parents[1])
        assert "parents[2]" in config_content, "config.py should use parents[2] for src layout"

        # Old flat layout: template scaffold files should be gone, but copier's
        # 3-way merge may preserve user-added files (not from template) in old location.
        # This is expected copier behavior - it doesn't delete non-template files.
        if flat_module.is_dir():
            old_files = [f.name for f in flat_module.rglob("*") if f.is_file()]
            # Only user-added files should remain (not template scaffold)
            scaffold_files = {"__init__.py", "config.py", "dataset.py", "features.py", "plots.py"}
            remaining_scaffold = set(old_files) & scaffold_files
            assert not remaining_scaffold, (
                f"Template scaffold files should not remain in old location: {remaining_scaffold}"
            )

        # pyproject.toml should have src layout config
        pyproject = (project_path / "pyproject.toml").read_text()
        assert 'where = ["src"]' in pyproject, "pyproject.toml should have src layout"

        # Migration warning should have been printed
        combined_output = result.stdout + result.stderr
        assert "Migration" in combined_output or "migration" in combined_output, (
            "Migration warning should be printed during update"
        )
