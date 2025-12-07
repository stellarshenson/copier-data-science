import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from itertools import cycle, product
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[1].resolve()
COPIER_DIR = REPO_ROOT  # copier.yml is at repo root
VENV_BIN = REPO_ROOT / ".venv" / "bin"


def get_copier_cmd():
    """Find the copier executable - check venv first, then system PATH."""
    venv_copier = VENV_BIN / "copier"
    if venv_copier.exists():
        return str(venv_copier)
    # Fall back to system copier (shutil.which checks PATH)
    system_copier = shutil.which("copier")
    if system_copier:
        return system_copier
    raise RuntimeError("copier not found in .venv/bin or system PATH")


default_args = {
    "project_name": "my_test_project",
    "repo_name": "my-test-repo",
    "module_name": "lib_project_module",
    "author_name": "DrivenData",
    "description": "A test project",
    # env_name is set per test config to avoid conflicts
}


# Configuration options from copier.yml
CONFIG_OPTIONS = {
    "environment_manager": ["uv", "conda", "virtualenv", "none"],
    "env_location": ["local", "global"],
    "dependency_file": ["pyproject.toml", "requirements.txt", "environment.yml"],
    "pydata_packages": ["none", "basic"],
    "include_code_scaffold": ["Yes", "No"],
    "linting_and_formatting": ["ruff", "flake8+black+isort"],
    "open_source_license": ["MIT", "BSD-3-Clause", "No license file"],
    "docs": ["mkdocs", "none"],
    "testing_framework": ["pytest", "unittest", "none"],
    "jupyter_kernel_support": ["Yes", "No"],
}


def config_generator(fast=False):
    """Generate test configurations for template testing."""
    # Python version - match the running version
    running_py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    py_version = [("python_version_number", v) for v in [running_py_version]]

    configs = product(
        py_version,
        [("environment_manager", opt) for opt in CONFIG_OPTIONS["environment_manager"]],
        [("env_location", opt) for opt in CONFIG_OPTIONS["env_location"]],
        [("dependency_file", opt) for opt in CONFIG_OPTIONS["dependency_file"]],
        [("pydata_packages", opt) for opt in CONFIG_OPTIONS["pydata_packages"]],
    )

    def _is_valid(config):
        config = dict(config)
        # env_location only applies to conda (global is invalid for non-conda)
        if (config["environment_manager"] != "conda") and (config["env_location"] == "global"):
            return False
        # environment.yml only valid for conda
        if (config["environment_manager"] != "conda") and (
            config["dependency_file"] == "environment.yml"
        ):
            return False
        return True

    # remove invalid configs
    configs = [c for c in configs if _is_valid(c)]

    # ensure linting and formatting options are run on code scaffold
    # otherwise, linting "passes" because one linter never runs on any code during tests
    code_format_cycler = cycle(
        product(
            [("include_code_scaffold", opt) for opt in CONFIG_OPTIONS["include_code_scaffold"]],
            [("linting_and_formatting", opt) for opt in CONFIG_OPTIONS["linting_and_formatting"]],
        )
    )

    # cycle over values for multi-select fields that should be inter-operable
    # and that we don't need to handle with combinatorics
    cycle_fields = [
        "open_source_license",
        "docs",
        "testing_framework",
        "jupyter_kernel_support",
    ]
    multi_select_cyclers = {k: cycle(CONFIG_OPTIONS[k]) for k in cycle_fields}

    for ind, c in enumerate(configs):
        config = dict(c)
        config.update(default_args)

        code_format_settings = dict(next(code_format_cycler))
        config.update(code_format_settings)

        for field, cycler in multi_select_cyclers.items():
            config[field] = next(cycler)

        # Copier uses flat dataset_storage
        config["dataset_storage"] = "none"
        config["s3_bucket"] = ""
        config["s3_aws_profile"] = "default"
        config["azure_container"] = ""
        config["gcs_bucket"] = ""

        # Additional copier-specific defaults
        config["env_encryption"] = "No"  # Skip encryption for tests
        config["custom_config"] = ""

        config["repo_name"] += f"-{ind}"
        # Set env_name to match repo_name to avoid conflicts between tests
        config["env_name"] = config["repo_name"].replace("-", "_")
        yield config

        # just do a single config if fast passed once or three times
        if fast == 1 or fast >= 3:
            break


def pytest_addoption(parser):
    """Pass -F/--fast multiple times to speed up tests

    default - execute makefile commands, all configs

     -F - execute makefile commands, single config
     -FF - skip makefile commands, all configs
     -FFF - skip makefile commands, single config
    """
    parser.addoption(
        "--fast",
        "-F",
        action="count",
        default=0,
        help="Speed up tests by skipping configs and/or Makefile validation",
    )


@pytest.fixture
def fast(request):
    return request.config.getoption("--fast")


def pytest_generate_tests(metafunc):
    # setup config fixture to get all of the results from config_generator
    def make_test_id(config):
        env_loc = config.get("env_location", "local")
        return f"{config['environment_manager']}-{env_loc}-{config['dependency_file']}-{config['pydata_packages']}"

    if "config" in metafunc.fixturenames:
        metafunc.parametrize(
            "config",
            config_generator(metafunc.config.getoption("fast")),
            ids=make_test_id,
        )


@contextmanager
def bake_project(config):
    """Context manager to create a project with Copier and clean up after."""
    temp = Path(tempfile.mkdtemp(suffix="data-project")).resolve()
    project_dir = temp / config["repo_name"]

    # Build copier command with data arguments
    cmd = [
        get_copier_cmd(),
        "copy",
        "--trust",
        "--defaults",
        str(COPIER_DIR),
        str(project_dir),
    ]

    # Add all config values as --data arguments
    for key, value in config.items():
        if key in ("repo_name",):
            continue  # Skip repo_name as it's the output dir
        # Convert Python bools/None to strings
        if isinstance(value, bool):
            value = str(value).lower()
        elif value is None:
            value = ""
        cmd.extend(["--data", f"{key}={value}"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=temp,
    )

    if result.returncode != 0:
        print(f"Copier command failed:\n{' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"Copier failed with return code {result.returncode}")

    yield project_dir

    # cleanup after
    shutil.rmtree(temp)
