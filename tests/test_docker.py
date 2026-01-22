"""Docker integration tests for the Copier template.

These tests verify that:
- make docker_build creates a valid Docker image
- make docker_run executes successfully
- Both uv and pip package managers work in Docker

Tests are skipped if Docker is not available or not running.
"""

import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import bake_project

# Check if Docker is available
DOCKER_AVAILABLE = shutil.which("docker") is not None


def docker_is_running():
    """Check if Docker daemon is running."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


DOCKER_RUNNING = docker_is_running()

# Skip all tests in this module if Docker is not available or not running
pytestmark = pytest.mark.skipif(
    not DOCKER_RUNNING,
    reason="Docker is not available or not running",
)


# Base test configuration with docker_support enabled
DOCKER_CONFIG_BASE = {
    "project_name": "docker_test_project",
    "repo_name": "docker_test_project",
    "module_name": "lib_docker_test_project",
    "author_name": "Test Author",
    "description": "Test project for Docker",
    "open_source_license": "MIT",
    "python_version_number": "3.12",
    "environment_manager": "uv",
    "dependency_file": "requirements.txt",
    "include_code_scaffold": "Yes",
    "docs": "none",
    "testing_framework": "pytest",
    "linting_and_formatting": "ruff",
    "docker_support": "Yes",
    "env_encryption": "No",
    # Copier-specific flat storage options
    "dataset_storage": "none",
    "s3_bucket": "",
    "s3_aws_profile": "default",
    "azure_container": "",
    "gcs_bucket": "",
    "custom_config": "",
    "pydata_packages": "none",
    "jupyter_kernel_support": "No",
    "env_name": "docker_test_project",
    "env_location": "local",
}


def run_docker_workflow(project_directory, package_manager):
    """Run the full Docker workflow and return results."""
    # Verify docker files exist
    dockerfile = project_directory / "docker" / "Dockerfile"
    entrypoint = project_directory / "docker" / "entrypoint.py"
    assert dockerfile.exists(), "Dockerfile should exist"
    assert entrypoint.exists(), "entrypoint.py should exist"

    # Verify Dockerfile contains expected package manager
    dockerfile_content = dockerfile.read_text()
    if package_manager == "uv":
        assert "ghcr.io/astral-sh/uv:latest" in dockerfile_content, "Dockerfile should use uv"
        assert "uv pip install" in dockerfile_content, "Dockerfile should use uv pip install"
    else:
        assert "pip install --no-cache-dir" in dockerfile_content, "Dockerfile should use pip"
        assert "ghcr.io/astral-sh/uv" not in dockerfile_content, "Dockerfile should not use uv"

    # Run make docker_run (which depends on docker_build -> build)
    result = subprocess.run(
        ["make", "docker_run"],
        cwd=project_directory,
        capture_output=True,
        timeout=300,  # 5 minute timeout for build
    )

    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")

    print(f"\n======================= {package_manager.upper()} STDOUT ======================")
    print(stdout)
    print(f"\n======================= {package_manager.upper()} STDERR ======================")
    print(stderr)

    return result, stdout, stderr


class TestDockerWorkflow:
    """Test Docker build and run workflow."""

    def test_docker_build_and_run_with_uv(self):
        """Test full Docker workflow with uv package manager."""
        config = DOCKER_CONFIG_BASE.copy()
        config["docker_package_manager"] = "uv"

        with bake_project(config) as project_directory:
            result, stdout, stderr = run_docker_workflow(project_directory, "uv")

            assert result.returncode == 0, (
                f"make docker_run (uv) failed with code {result.returncode}\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

            # Verify the container ran and printed the colourful message
            assert (
                "Running inside Docker container" in stdout
                or "Running inside Docker container" in stderr
            )
            assert "docker_test_project" in stdout or "docker_test_project" in stderr

    def test_docker_build_and_run_with_pip(self):
        """Test full Docker workflow with pip package manager."""
        config = DOCKER_CONFIG_BASE.copy()
        config["docker_package_manager"] = "pip"

        with bake_project(config) as project_directory:
            result, stdout, stderr = run_docker_workflow(project_directory, "pip")

            assert result.returncode == 0, (
                f"make docker_run (pip) failed with code {result.returncode}\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

            # Verify the container ran and printed the colourful message
            assert (
                "Running inside Docker container" in stdout
                or "Running inside Docker container" in stderr
            )
            assert "docker_test_project" in stdout or "docker_test_project" in stderr

    def test_docker_files_not_present_when_disabled(self):
        """Test that docker files are not created when docker_support is No."""
        config = DOCKER_CONFIG_BASE.copy()
        config["docker_support"] = "No"

        with bake_project(config) as project_directory:
            docker_dir = project_directory / "docker"
            assert not docker_dir.exists(), (
                "docker/ directory should not exist when docker_support=No"
            )


class TestDockerUpdateScenario:
    """Test enabling docker during copier update."""

    def test_docker_created_by_post_gen_when_missing(self, tmp_path):
        """Test that post_gen.py creates docker folder when docker_support=Yes but folder missing.

        This simulates the update scenario where:
        1. Project was created with docker_support=No (no docker folder)
        2. User runs update with docker_support=Yes
        3. post_gen.py should create and render the docker templates
        """
        import subprocess
        import sys

        # Create .copier-answers.yml to simulate existing project
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("_commit: v1.2.12\n")

        # Run post_gen.py with docker_support=Yes
        post_gen_script = Path(__file__).parent.parent / "scripts" / "post_gen.py"

        result = subprocess.run(
            [
                sys.executable,
                str(post_gen_script),
                "--project-name",
                "test_project",
                "--repo-name",
                "test_project",
                "--env-name",
                "test_project",
                "--module-name",
                "lib_test_project",
                "--author-name",
                "Test Author",
                "--description",
                "Test project",
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
                "Yes",
                "--docker-package-manager",
                "uv",
                "--package-repository",
                "No",
                "--package-repository-url",
                "",
                "--custom-config",
                "",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"post_gen.py failed: {result.stderr}"

        # Verify docker folder was created
        docker_dir = tmp_path / "docker"
        assert docker_dir.exists(), "docker/ should be created by post_gen.py"

        dockerfile = docker_dir / "Dockerfile"
        entrypoint = docker_dir / "entrypoint.py"
        assert dockerfile.exists(), "Dockerfile should exist"
        assert entrypoint.exists(), "entrypoint.py should exist"

        # Verify templates are rendered (not raw Jinja)
        dockerfile_content = dockerfile.read_text()
        assert "{{" not in dockerfile_content, "Dockerfile should be rendered, not raw template"
        assert "ghcr.io/astral-sh/uv:latest" in dockerfile_content, "Dockerfile should use uv"
        assert "PYTHON_VERSION=3.12" in dockerfile_content, (
            "Dockerfile should have correct Python version"
        )

        entrypoint_content = entrypoint.read_text()
        assert "{{" not in entrypoint_content, "entrypoint.py should be rendered, not raw template"
        assert "lib_test_project" in entrypoint_content, (
            "entrypoint.py should have correct module name"
        )

    def test_docker_not_created_when_disabled(self, tmp_path):
        """Test that post_gen.py does not create docker folder when docker_support=No."""
        import subprocess
        import sys

        # Create .copier-answers.yml to simulate existing project
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("_commit: v1.2.12\n")

        # Run post_gen.py with docker_support=No
        post_gen_script = Path(__file__).parent.parent / "scripts" / "post_gen.py"

        result = subprocess.run(
            [
                sys.executable,
                str(post_gen_script),
                "--project-name",
                "test_project",
                "--repo-name",
                "test_project",
                "--env-name",
                "test_project",
                "--module-name",
                "lib_test_project",
                "--author-name",
                "Test Author",
                "--description",
                "Test project",
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
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"post_gen.py failed: {result.stderr}"

        # Verify docker folder was NOT created
        docker_dir = tmp_path / "docker"
        assert not docker_dir.exists(), "docker/ should NOT be created when docker_support=No"


class TestDockerUpdateIntegration:
    """Integration tests for docker update using actual copier update.

    These tests verify the full copier update workflow, not just post_gen.py.
    They require network access to fetch from GitHub and are marked accordingly.

    See .claude/COPIER_UPDATE_TESTING.md for methodology documentation.
    """

    @pytest.mark.integration
    def test_docker_enabled_during_copier_update(self, tmp_path):
        """Test enabling docker_support during actual copier update.

        Full integration test that:
        1. Creates project at v1.2.15 with docker_support=No
        2. Initializes git (required for copier update)
        3. Runs copier update to v1.2.18+ with docker_support=Yes
        4. Verifies docker folder is created with rendered templates
        """
        project_path = tmp_path / "test-docker-update"

        # Step 1: Create project at old version without docker
        result = subprocess.run(
            [
                "copier",
                "copy",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "v1.2.15",
                "-d",
                "docker_support=No",
                "https://github.com/stellarshenson/copier-data-science.git",
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier copy failed: {result.stderr}"

        # Verify no docker folder initially
        docker_dir = project_path / "docker"
        assert not docker_dir.exists(), "docker/ should not exist after initial creation"

        # Step 2: Initialize git (required for copier update)
        subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=project_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"], cwd=project_path, check=True, capture_output=True
        )

        # Step 3: Update to newer version with docker enabled
        result = subprocess.run(
            [
                "copier",
                "update",
                "--trust",
                "--defaults",
                "--vcs-ref",
                "v1.2.18",
                "-d",
                "docker_support=Yes",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"copier update failed: {result.stderr}"

        # Step 4: Verify docker folder was created
        assert docker_dir.exists(), "docker/ should exist after update with docker_support=Yes"

        dockerfile = docker_dir / "Dockerfile"
        entrypoint = docker_dir / "entrypoint.py"
        assert dockerfile.exists(), "Dockerfile should exist"
        assert entrypoint.exists(), "entrypoint.py should exist"

        # Verify templates are rendered correctly
        dockerfile_content = dockerfile.read_text()
        assert "{{" not in dockerfile_content, "Dockerfile should be rendered"
        assert "PYTHON_VERSION=3.12" in dockerfile_content

        entrypoint_content = entrypoint.read_text()
        assert "{{" not in entrypoint_content, "entrypoint.py should be rendered"
        assert "lib_test_docker_update" in entrypoint_content
