"""Docker integration tests for the Copier template.

These tests verify that:
- make docker_build creates a valid Docker image
- make docker_run executes successfully
- Both uv and pip package managers work in Docker

Tests are skipped if Docker is not available or not running.
"""

import shutil
import subprocess

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
            assert (
                not docker_dir.exists()
            ), "docker/ directory should not exist when docker_support=No"
