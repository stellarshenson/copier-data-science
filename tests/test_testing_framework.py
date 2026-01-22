"""Tests for testing framework handling during copier updates.

These tests verify that enabling testing during copier update (from testing_framework=none)
correctly creates the tests folder with rendered templates.

Pattern matches test_docker.py for similar configuration-driven folder creation scenarios.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[1].resolve()
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class TestTestingFrameworkUpdateScenario:
    """Test enabling testing framework during copier update from testing_framework=none."""

    def test_tests_created_by_post_gen_when_missing(self, tmp_path):
        """Test that post_gen.py creates tests folder when testing_framework!=none but folder missing.

        Simulates update scenario:
        1. Project initially created with testing_framework=none (no tests folder)
        2. User updates config to testing_framework=pytest
        3. Post_gen.py should create tests folder with rendered pytest templates
        """
        # Simulate project structure without tests folder
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        # Create minimal project structure
        (project_path / "lib_test_module").mkdir()
        (project_path / "lib_test_module" / "__init__.py").write_text("")

        # Run post_gen.py with testing_framework=pytest
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "post_gen.py"),
                "--project-name",
                "Test Project",
                "--repo-name",
                "test-project",
                "--env-name",
                "test_project",
                "--module-name",
                "lib_test_module",
                "--author-name",
                "Test Author",
                "--description",
                "Test description",
                "--python-version",
                "3.12",
                "--dataset-storage",
                "none",
                "--s3-bucket",
                "",
                "--s3-aws-profile",
                "default",
                "--azure-container",
                "",
                "--gcs-bucket",
                "",
                "--environment-manager",
                "uv",
                "--env-location",
                "local",
                "--dependency-file",
                "pyproject.toml",
                "--pydata-packages",
                "none",
                "--testing-framework",
                "pytest",
                "--linting-and-formatting",
                "ruff",
                "--open-source-license",
                "MIT",
                "--docs",
                "none",
                "--include-code-scaffold",
                "Yes",
                "--jupyter-kernel-support",
                "No",
                "--env-encryption",
                "No",
                "--docker-support",
                "No",
                "--docker-package-manager",
                "uv",
                "--package-repository",
                "No",
                "--package-repository-url",
                "",
                "--custom-config",
                "",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"post_gen.py failed: {result.stderr}"

        # Verify tests folder was created
        tests_dir = project_path / "tests"
        assert tests_dir.exists(), "tests/ should be created when testing_framework=pytest"
        assert tests_dir.is_dir(), "tests/ should be a directory"

        # Verify pytest template files were rendered
        test_data = tests_dir / "test_data.py"
        assert test_data.exists(), "tests/test_data.py should exist"

        # Check for rendered content (no raw Jinja2 variables)
        if test_data.exists():
            content = test_data.read_text()
            assert "{{" not in content, "Template should be rendered, not contain {{ }}"
            assert "}}" not in content, "Template should be rendered, not contain {{ }}"
            assert "pytest" in content, "test_data.py should contain pytest code"

    def test_tests_created_for_unittest(self, tmp_path):
        """Test that post_gen.py creates tests folder with unittest templates."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        (project_path / "lib_test_module").mkdir()
        (project_path / "lib_test_module" / "__init__.py").write_text("")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "post_gen.py"),
                "--project-name",
                "Test Project",
                "--repo-name",
                "test-project",
                "--env-name",
                "test_project",
                "--module-name",
                "lib_test_module",
                "--author-name",
                "Test Author",
                "--description",
                "Test description",
                "--python-version",
                "3.12",
                "--dataset-storage",
                "none",
                "--s3-bucket",
                "",
                "--s3-aws-profile",
                "default",
                "--azure-container",
                "",
                "--gcs-bucket",
                "",
                "--environment-manager",
                "virtualenv",
                "--env-location",
                "local",
                "--dependency-file",
                "pyproject.toml",
                "--pydata-packages",
                "none",
                "--testing-framework",
                "unittest",
                "--linting-and-formatting",
                "ruff",
                "--open-source-license",
                "MIT",
                "--docs",
                "none",
                "--include-code-scaffold",
                "Yes",
                "--jupyter-kernel-support",
                "No",
                "--env-encryption",
                "No",
                "--docker-support",
                "No",
                "--docker-package-manager",
                "uv",
                "--package-repository",
                "No",
                "--package-repository-url",
                "",
                "--custom-config",
                "",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"post_gen.py failed: {result.stderr}"

        tests_dir = project_path / "tests"
        assert tests_dir.exists(), "tests/ should be created when testing_framework=unittest"

        test_data = tests_dir / "test_data.py"
        assert test_data.exists(), "tests/test_data.py should exist for unittest"

    def test_tests_not_created_when_disabled(self, tmp_path):
        """Test that tests folder is NOT created when testing_framework=none."""
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        (project_path / "lib_test_module").mkdir()
        (project_path / "lib_test_module" / "__init__.py").write_text("")

        # Create a tests folder that should be deleted
        tests_dir = project_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "dummy.py").write_text("# This should be deleted")

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "post_gen.py"),
                "--project-name",
                "Test Project",
                "--repo-name",
                "test-project",
                "--env-name",
                "test_project",
                "--module-name",
                "lib_test_module",
                "--author-name",
                "Test Author",
                "--description",
                "Test description",
                "--python-version",
                "3.12",
                "--dataset-storage",
                "none",
                "--s3-bucket",
                "",
                "--s3-aws-profile",
                "default",
                "--azure-container",
                "",
                "--gcs-bucket",
                "",
                "--environment-manager",
                "none",
                "--env-location",
                "local",
                "--dependency-file",
                "pyproject.toml",
                "--pydata-packages",
                "none",
                "--testing-framework",
                "none",
                "--linting-and-formatting",
                "ruff",
                "--open-source-license",
                "MIT",
                "--docs",
                "none",
                "--include-code-scaffold",
                "No",
                "--jupyter-kernel-support",
                "No",
                "--env-encryption",
                "No",
                "--docker-support",
                "No",
                "--docker-package-manager",
                "uv",
                "--package-repository",
                "No",
                "--package-repository-url",
                "",
                "--custom-config",
                "",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"post_gen.py failed: {result.stderr}"

        # Verify tests folder was deleted
        assert (
            not tests_dir.exists()
        ), "tests/ should NOT exist when testing_framework=none"


class TestTestingFrameworkUpdateIntegration:
    """Integration tests for testing framework update using actual copier update.

    These tests verify the full copier update workflow with actual GitHub tags.
    Pattern matches TestDockerUpdateIntegration from test_docker.py.
    """

    @pytest.mark.integration
    def test_testing_enabled_during_copier_update(self, tmp_path):
        """Test enabling testing_framework during actual copier update.

        Full integration test that:
        1. Creates project at v1.2.14 with testing_framework=none
        2. Initializes git (required for copier update)
        3. Runs copier update to HEAD with testing_framework=pytest
        4. Verifies tests folder is created with rendered templates
        """
        project_path = tmp_path / "test-testing-update"

        # Step 1: Create project at v1.2.15 (has tests folder deletion fix) without testing
        result = subprocess.run(
            [
                "copier",
                "copy",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "v1.2.15",
                "-d",
                "testing_framework=none",
                "https://github.com/stellarshenson/copier-data-science.git",
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Verify no tests folder initially (v1.2.15+ correctly deletes it)
        tests_dir = project_path / "tests"
        assert (
            not tests_dir.exists()
        ), "tests/ should not exist after creation with testing_framework=none at v1.2.15+"

        # Step 2: Initialize git (required for copier update)
        subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "add", "-A"], cwd=project_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )

        # Step 3: Update to HEAD with testing enabled
        result = subprocess.run(
            [
                "copier",
                "update",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "HEAD",
                "-d",
                "testing_framework=pytest",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier update failed: {result.stderr}"

        # Step 4: Verify tests folder was created with rendered templates
        assert tests_dir.exists(), "tests/ should be created after update to testing_framework=pytest"
        assert tests_dir.is_dir(), "tests/ should be a directory"

        # Check for pytest template files
        test_data = tests_dir / "test_data.py"
        assert test_data.exists(), "tests/test_data.py should exist after update"

        # Verify templates are rendered (no raw Jinja2)
        if test_data.exists():
            content = test_data.read_text()
            assert "{{" not in content, "Templates should be rendered after update"
            assert "}}" not in content, "Templates should be rendered after update"
