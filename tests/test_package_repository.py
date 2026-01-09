"""Package repository configuration tests for the Copier template.

These tests verify that:
- When package_repository=Yes: PACKAGE_REPOSITORY, publish target, and twine are present
- When package_repository=No: None of these are included in the generated project
- Twine is correctly added to dev dependencies based on dependency_file type
"""

import pytest
from conftest import bake_project

# Base test configuration
PKG_REPO_CONFIG_BASE = {
    "project_name": "pkg_repo_test",
    "repo_name": "pkg_repo_test",
    "module_name": "lib_pkg_repo_test",
    "author_name": "Test Author",
    "description": "Test project for package repository",
    "open_source_license": "MIT",
    "python_version_number": "3.12",
    "environment_manager": "uv",
    "dependency_file": "pyproject.toml",
    "include_code_scaffold": "Yes",
    "docs": "none",
    "testing_framework": "pytest",
    "linting_and_formatting": "ruff",
    "docker_support": "No",
    "env_encryption": "No",
    "dataset_storage": "none",
    "s3_bucket": "",
    "s3_aws_profile": "default",
    "azure_container": "",
    "gcs_bucket": "",
    "custom_config": "",
    "pydata_packages": "none",
    "jupyter_kernel_support": "No",
    "env_name": "pkg_repo_test",
    "env_location": "local",
}


class TestPackageRepositoryEnabled:
    """Tests when package_repository=Yes."""

    def test_makefile_has_package_repository_variable(self):
        """Test that PACKAGE_REPOSITORY variable is in Makefile when enabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://test.pypi.org/legacy/"

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            assert "PACKAGE_REPOSITORY = https://test.pypi.org/legacy/" in content, (
                "PACKAGE_REPOSITORY variable should be set to the configured URL"
            )

    def test_makefile_has_publish_target(self):
        """Test that publish target is in Makefile when enabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://test.pypi.org/legacy/"

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            assert "publish:" in content, "publish target should exist"
            assert "twine upload" in content, "publish target should use twine"
            assert "publish" in content.split("\n")[0], "publish should be in .PHONY"

    def test_twine_in_pyproject_toml_dev_deps(self):
        """Test that twine is in pyproject.toml dev dependencies when using pyproject.toml."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://test.pypi.org/legacy/"
        config["dependency_file"] = "pyproject.toml"

        with bake_project(config) as project_dir:
            pyproject = project_dir / "pyproject.toml"
            content = pyproject.read_text()

            assert '"twine"' in content, "twine should be in pyproject.toml dev dependencies"

    def test_twine_in_requirements_dev_txt(self):
        """Test that twine is in requirements-dev.txt when using requirements.txt."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://test.pypi.org/legacy/"
        config["dependency_file"] = "requirements.txt"

        with bake_project(config) as project_dir:
            requirements_dev = project_dir / "requirements-dev.txt"
            content = requirements_dev.read_text()

            assert "twine" in content, "twine should be in requirements-dev.txt"

    def test_twine_in_environment_yml(self):
        """Test that twine is in environment.yml when using conda with environment.yml."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://test.pypi.org/legacy/"
        config["environment_manager"] = "conda"
        config["dependency_file"] = "environment.yml"

        with bake_project(config) as project_dir:
            env_yml = project_dir / "environment.yml"
            content = env_yml.read_text()

            assert "twine" in content, "twine should be in environment.yml dependencies"

    @pytest.mark.parametrize("env_manager", ["uv", "virtualenv", "conda"])
    def test_publish_target_for_each_env_manager(self, env_manager):
        """Test that publish target works for all environment managers."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://test.pypi.org/legacy/"
        config["environment_manager"] = env_manager
        config["repo_name"] = f"pkg_repo_{env_manager}"
        config["env_name"] = f"pkg_repo_{env_manager}"

        # Use appropriate dependency file for conda
        if env_manager == "conda":
            config["dependency_file"] = "pyproject.toml"

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            assert "publish: build" in content, (
                f"publish target should depend on build for {env_manager}"
            )
            assert "PACKAGE_REPOSITORY" in content, (
                f"PACKAGE_REPOSITORY variable should exist for {env_manager}"
            )


class TestPackageRepositoryDisabled:
    """Tests when package_repository=No (default)."""

    def test_makefile_no_package_repository_variable(self):
        """Test that PACKAGE_REPOSITORY variable is NOT in Makefile when disabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "No"

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            assert "PACKAGE_REPOSITORY" not in content, (
                "PACKAGE_REPOSITORY variable should not exist when disabled"
            )

    def test_makefile_no_publish_target(self):
        """Test that publish target is NOT in Makefile when disabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "No"

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            # Check that "publish:" target doesn't exist
            # (but "publish" might appear in comments or other contexts)
            lines = content.split("\n")
            publish_targets = [line for line in lines if line.startswith("publish:")]
            assert len(publish_targets) == 0, "publish target should not exist"

            # Also verify publish is not in .PHONY
            phony_line = lines[0] if lines[0].startswith(".PHONY") else ""
            assert " publish" not in phony_line, "publish should not be in .PHONY"

    def test_twine_not_in_pyproject_toml(self):
        """Test that twine is NOT in pyproject.toml when disabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "No"
        config["dependency_file"] = "pyproject.toml"

        with bake_project(config) as project_dir:
            pyproject = project_dir / "pyproject.toml"
            content = pyproject.read_text()

            assert "twine" not in content, "twine should not be in pyproject.toml when disabled"

    def test_twine_not_in_requirements_dev_txt(self):
        """Test that twine is NOT in requirements-dev.txt when disabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "No"
        config["dependency_file"] = "requirements.txt"

        with bake_project(config) as project_dir:
            requirements_dev = project_dir / "requirements-dev.txt"
            content = requirements_dev.read_text()

            assert "twine" not in content, (
                "twine should not be in requirements-dev.txt when disabled"
            )

    def test_twine_not_in_environment_yml(self):
        """Test that twine is NOT in environment.yml when disabled."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "No"
        config["environment_manager"] = "conda"
        config["dependency_file"] = "environment.yml"

        with bake_project(config) as project_dir:
            env_yml = project_dir / "environment.yml"
            content = env_yml.read_text()

            assert "twine" not in content, "twine should not be in environment.yml when disabled"


class TestPackageRepositoryUrlHandling:
    """Tests for package_repository_url handling."""

    def test_empty_url_still_creates_variable(self):
        """Test that empty URL still creates PACKAGE_REPOSITORY variable."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = ""

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            # Variable should exist but be empty
            assert "PACKAGE_REPOSITORY =" in content, (
                "PACKAGE_REPOSITORY variable should exist even with empty URL"
            )

    def test_custom_repository_url(self):
        """Test that custom repository URL is correctly set."""
        config = PKG_REPO_CONFIG_BASE.copy()
        config["package_repository"] = "Yes"
        config["package_repository_url"] = "https://my-private-pypi.example.com/simple/"

        with bake_project(config) as project_dir:
            makefile = project_dir / "Makefile"
            content = makefile.read_text()

            assert "https://my-private-pypi.example.com/simple/" in content, (
                "Custom repository URL should be in Makefile"
            )
