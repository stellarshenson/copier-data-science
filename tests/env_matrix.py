"""
Environment specification matrix for copier-data-science tests.

This module defines the expected files and configurations for each
environment_manager + dependency_file combination. Used by tests to
verify correct file generation.

See docs/docs/env-management.md for the full matrix documentation.
"""

# Files that are ALWAYS present regardless of configuration
ALWAYS_PRESENT = [
    "Makefile",
    "README.md",
    "pyproject.toml",  # Always present for metadata/tools (deps section conditional)
    ".env",
    ".gitignore",
    "data/external/.gitkeep",
    "data/interim/.gitkeep",
    "data/processed/.gitkeep",
    "data/raw/.gitkeep",
    "docs/.gitkeep",
    "notebooks/.gitkeep",
    "references/.gitkeep",
    "reports/.gitkeep",
    "reports/figures/.gitkeep",
    "models/.gitkeep",
]

# Environment specification matrix
# Key: (environment_manager, dependency_file)
# Value: dict with expected files and pyproject.toml content expectations
ENV_MATRIX = {
    # ==================== CONDA ====================
    ("conda", "requirements.txt"): {
        "files_present": [
            "requirements.txt",
            "requirements-dev.txt",
        ],
        "files_absent": [
            "environment.yml",
        ],
        "pyproject_has_deps": False,
        "pyproject_has_dev_deps": False,
        "description": "Conda with pip-based deps in requirements files",
    },
    ("conda", "pyproject.toml"): {
        "files_present": [],
        "files_absent": [
            "requirements.txt",
            "requirements-dev.txt",
            "environment.yml",
        ],
        "pyproject_has_deps": True,
        "pyproject_has_dev_deps": True,
        "description": "Conda with modern Python packaging",
    },
    ("conda", "environment.yml"): {
        "files_present": [
            "environment.yml",
        ],
        "files_absent": [
            "requirements.txt",
            "requirements-dev.txt",
        ],
        "pyproject_has_deps": True,
        "pyproject_has_dev_deps": False,  # Dev deps in environment.yml
        "description": "Conda-native workflow with dev deps in environment.yml",
    },
    # ==================== UV ====================
    ("uv", "requirements.txt"): {
        "files_present": [
            "requirements.txt",
            "requirements-dev.txt",
        ],
        "files_absent": [
            "environment.yml",
        ],
        "pyproject_has_deps": False,
        "pyproject_has_dev_deps": False,
        "description": "UV with pip-based deps in requirements files",
    },
    ("uv", "pyproject.toml"): {
        "files_present": [],
        "files_absent": [
            "requirements.txt",
            "requirements-dev.txt",
            "environment.yml",
        ],
        "pyproject_has_deps": True,
        "pyproject_has_dev_deps": True,
        "description": "UV with modern Python packaging",
    },
    # ==================== VIRTUALENV ====================
    ("virtualenv", "requirements.txt"): {
        "files_present": [
            "requirements.txt",
            "requirements-dev.txt",
        ],
        "files_absent": [
            "environment.yml",
        ],
        "pyproject_has_deps": False,
        "pyproject_has_dev_deps": False,
        "description": "Virtualenv with pip-based deps in requirements files",
    },
    ("virtualenv", "pyproject.toml"): {
        "files_present": [],
        "files_absent": [
            "requirements.txt",
            "requirements-dev.txt",
            "environment.yml",
        ],
        "pyproject_has_deps": True,
        "pyproject_has_dev_deps": True,
        "description": "Virtualenv with modern Python packaging",
    },
    # ==================== NONE ====================
    ("none", "requirements.txt"): {
        "files_present": [
            "requirements.txt",
        ],
        "files_absent": [
            "requirements-dev.txt",  # No dev deps for 'none' env manager
            "environment.yml",
        ],
        "pyproject_has_deps": False,
        "pyproject_has_dev_deps": False,
        "description": "No environment manager with requirements.txt",
    },
    ("none", "pyproject.toml"): {
        "files_present": [],
        "files_absent": [
            "requirements.txt",
            "requirements-dev.txt",
            "environment.yml",
        ],
        "pyproject_has_deps": True,
        "pyproject_has_dev_deps": False,  # No dev deps for 'none' env manager
        "description": "No environment manager with pyproject.toml",
    },
}


def get_env_spec(environment_manager: str, dependency_file: str) -> dict:
    """Get the environment specification for a given configuration.

    Args:
        environment_manager: One of 'conda', 'uv', 'virtualenv', 'none'
        dependency_file: One of 'requirements.txt', 'pyproject.toml', 'environment.yml'

    Returns:
        Dict with files_present, files_absent, pyproject expectations

    Raises:
        KeyError: If the combination is invalid (e.g., uv + environment.yml)
    """
    key = (environment_manager, dependency_file)
    if key not in ENV_MATRIX:
        raise KeyError(
            f"Invalid combination: {environment_manager} + {dependency_file}. "
            "environment.yml is only valid for conda."
        )
    return ENV_MATRIX[key]


def is_valid_combination(environment_manager: str, dependency_file: str) -> bool:
    """Check if an environment_manager + dependency_file combination is valid.

    Args:
        environment_manager: One of 'conda', 'uv', 'virtualenv', 'none'
        dependency_file: One of 'requirements.txt', 'pyproject.toml', 'environment.yml'

    Returns:
        True if the combination is valid, False otherwise
    """
    return (environment_manager, dependency_file) in ENV_MATRIX


def get_expected_files(config: dict) -> list:
    """Get list of expected files for a given configuration.

    Args:
        config: Test configuration dict with environment_manager, dependency_file, etc.

    Returns:
        List of expected file paths
    """
    env_manager = config["environment_manager"]
    dep_file = config["dependency_file"]

    spec = get_env_spec(env_manager, dep_file)

    expected = list(ALWAYS_PRESENT)
    expected.extend(spec["files_present"])

    # Add module __init__.py
    expected.append(f"{config['module_name']}/__init__.py")

    # Conditional files based on other config options
    if not config.get("open_source_license", "MIT").startswith("No license"):
        expected.append("LICENSE")

    if config.get("linting_and_formatting") == "flake8+black+isort":
        expected.append("setup.cfg")

    if config.get("include_code_scaffold") == "Yes":
        expected.extend(
            [
                f"{config['module_name']}/config.py",
                f"{config['module_name']}/dataset.py",
                f"{config['module_name']}/features.py",
                f"{config['module_name']}/modeling/__init__.py",
                f"{config['module_name']}/modeling/train.py",
                f"{config['module_name']}/modeling/predict.py",
                f"{config['module_name']}/plots.py",
            ]
        )

    if config.get("docs") == "mkdocs":
        expected.extend(
            [
                "docs/mkdocs.yml",
                "docs/README.md",
                "docs/docs/index.md",
                "docs/docs/getting-started.md",
            ]
        )

    if config.get("testing_framework", "pytest") != "none":
        expected.append("tests/test_data.py")

    return expected


def get_absent_files(config: dict) -> list:
    """Get list of files that should NOT exist for a given configuration.

    Args:
        config: Test configuration dict with environment_manager, dependency_file, etc.

    Returns:
        List of file paths that should not exist
    """
    env_manager = config["environment_manager"]
    dep_file = config["dependency_file"]

    spec = get_env_spec(env_manager, dep_file)
    return spec["files_absent"]
