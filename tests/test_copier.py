"""
Tests for Copier template generation.

Tests project generation with various configuration combinations,
verifying correct file structure and content rendering.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import bake_project, config_generator
from env_matrix import get_absent_files, get_expected_files

BASH_EXECUTABLE = os.getenv("BASH_EXECUTABLE", "bash")


def is_copier_available():
    """Check if copier is installed."""
    try:
        result = subprocess.run(
            ["copier", "--version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


# Skip all tests if copier is not installed
pytestmark = pytest.mark.skipif(
    not is_copier_available(),
    reason="copier not installed",
)


def _decode_print_stdout_stderr(result):
    """Print command stdout and stderr to console to use when debugging failing tests
    Normally hidden by pytest except in failure we want this displayed
    """
    encoding = sys.stdout.encoding

    if encoding is None:
        encoding = "utf-8"

    print("\n======================= STDOUT ======================")
    stdout = result.stdout.decode(encoding)
    print(stdout)

    print("\n======================= STDERR ======================")
    stderr = result.stderr.decode(encoding)
    print(stderr)

    return stdout, stderr


def no_curlies(filepath):
    """Utility to make sure no curly braces appear in a file.
    That is, was Jinja able to render everything?
    """
    data = filepath.open("r").read()

    template_strings = ["{{", "}}", "{%", "%}"]

    template_strings_in_file = [s in data for s in template_strings]
    return not any(template_strings_in_file)


def test_baking_configs(config, fast):
    """For every generated config in the config_generator, run all
    of the tests.
    """
    print("using config", json.dumps(config, indent=2))
    with bake_project(config) as project_directory:
        verify_folders(project_directory, config)
        verify_files(project_directory, config)

        if fast < 2:
            verify_makefile_commands(project_directory, config)


def verify_folders(root, config):
    """Tests that expected folders and only expected folders exist."""
    expected_dirs = [
        ".",
        "data",
        "data/external",
        "data/interim",
        "data/processed",
        "data/raw",
        "docs",
        "models",
        "notebooks",
        "references",
        "reports",
        "reports/figures",
        config["module_name"],
    ]

    if config["include_code_scaffold"] == "Yes":
        expected_dirs += [
            f"{config['module_name']}/modeling",
        ]

    if config["docs"] == "mkdocs":
        expected_dirs += ["docs/docs"]

    # Tests folder is created when testing_framework != "none"
    if config.get("testing_framework", "pytest") != "none":
        expected_dirs += ["tests"]

    expected_dirs = [Path(d) for d in expected_dirs]

    # Exclude .ipynb_checkpoints and __pycache__ directories
    excluded_dirs = {".ipynb_checkpoints", "__pycache__"}
    existing_dirs = [
        d.resolve().relative_to(root)
        for d in root.glob("**")
        if d.is_dir() and d.name not in excluded_dirs
    ]

    assert sorted(existing_dirs) == sorted(expected_dirs)


def verify_files(root, config):
    """Test that expected files and only expected files exist.

    Uses the ENV_MATRIX from env_matrix.py for environment-specific file expectations.
    See docs/docs/env-management.md for the full matrix documentation.
    """
    # Get expected files from the env_matrix
    expected_files = get_expected_files(config)

    # Copier adds .copier-answers.yml
    expected_files.append(".copier-answers.yml")

    expected_files = [Path(f) for f in expected_files]

    existing_files = [f.relative_to(root) for f in root.glob("**/*") if f.is_file()]

    assert sorted(existing_files) == sorted(set(expected_files)), (
        f"File mismatch for {config['environment_manager']} + {config['dependency_file']}\n"
        f"Missing: {set(expected_files) - set(existing_files)}\n"
        f"Extra: {set(existing_files) - set(expected_files)}"
    )

    # Verify files that should NOT exist (from env_matrix)
    absent_files = get_absent_files(config)
    for absent_file in absent_files:
        assert not (root / absent_file).exists(), (
            f"{absent_file} should not exist for "
            f"{config['environment_manager']} + {config['dependency_file']}"
        )

    # Verify no unrendered Jinja templates
    for f in existing_files:
        # Skip .copier-answers.yml as it contains template syntax documentation
        if f.name == ".copier-answers.yml":
            continue
        assert no_curlies(root / f), f"Unrendered Jinja template in {f}"


def verify_makefile_commands(root, config):
    """Actually shell out to bash and run the make commands for:
    - blank command listing commands
    - create_environment
    - requirements
    - linting
    - formatting
    - install (conda only)
    - clean
    - remove_environment (conda only)
    Ensure that these use the proper environment.
    """
    test_path = Path(__file__).parent

    if config["environment_manager"] == "conda":
        harness_path = test_path / "conda_harness.sh"
    elif config["environment_manager"] == "virtualenv":
        harness_path = test_path / "virtualenv_harness.sh"
    elif config["environment_manager"] == "uv":
        harness_path = test_path / "uv_harness.sh"
    elif config["environment_manager"] == "none":
        return True
    else:
        raise ValueError(
            f"Environment manager '{config['environment_manager']}' not found in test harnesses."
        )

    # Build command arguments
    cmd_args = [
        BASH_EXECUTABLE,
        str(harness_path),
        str(root.resolve()),
        str(config["module_name"]),
    ]

    # Pass env_location and env_name for conda
    if config["environment_manager"] == "conda":
        cmd_args.append(config.get("env_location", "local"))
        cmd_args.append(config.get("env_name", config["repo_name"]))

    result = subprocess.run(
        cmd_args,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    stdout_output, stderr_output = _decode_print_stdout_stderr(result)

    # Check that makefile help ran successfully
    assert "Available rules:" in stdout_output
    assert "clean" in stdout_output

    # Check that linting and formatting ran successfully
    if config["linting_and_formatting"] == "ruff":
        assert "All checks passed!" in stdout_output
        assert "left unchanged" in stdout_output
        assert "reformatted" not in stdout_output
    elif config["linting_and_formatting"] == "flake8+black+isort":
        assert "All done!" in stderr_output
        assert "left unchanged" in stderr_output
        assert "reformatted" not in stderr_output

    # Check that all targets passed (from harness)
    assert "All targets passed!" in stdout_output

    assert result.returncode == 0


def test_copier_answers_file_created(fast):
    """Test that .copier-answers.yml is created with correct content."""
    config = next(config_generator(fast=1))

    with bake_project(config) as project_dir:
        answers_file = project_dir / ".copier-answers.yml"
        assert answers_file.exists(), ".copier-answers.yml should be created"

        content = answers_file.read_text()
        # Verify key configuration values are recorded
        # Note: project_name has when: false, so it's auto-derived and not in answers
        assert "repo_name" in content
        assert "environment_manager" in content
        assert "dependency_file" in content
