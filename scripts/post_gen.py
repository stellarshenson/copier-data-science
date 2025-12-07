#!/usr/bin/env python3
"""
Post-generation script for Copier template.

This script performs cleanup and configuration similar to cookiecutter's
hooks/post_gen_project.py but reads configuration from command-line arguments
passed by Copier's _tasks.
"""

import argparse
import shutil
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
from zipfile import ZipFile

import tomlkit


#
#  HELPER FUNCTIONS
#
def resolve_python_version_specifier(python_version):
    """Resolves the user-provided Python version string to a version specifier."""
    version_parts = python_version.split(".")
    if len(version_parts) == 2:
        major, minor = version_parts
        patch = "0"
        operator = "~="
    elif len(version_parts) == 3:
        major, minor, patch = version_parts
        operator = "=="
    else:
        raise ValueError(
            f"Invalid Python version specifier {python_version}. "
            "Please specify version as <major>.<minor> or <major>.<minor>.<patch>, "
            "e.g., 3.10, 3.10.1, etc."
        )

    resolved_python_version = ".".join((major, minor, patch))
    return f"{operator}{resolved_python_version}"


def write_python_version(python_version):
    with open("pyproject.toml", "r") as f:
        doc = tomlkit.parse(f.read())

    doc["project"]["requires-python"] = resolve_python_version_specifier(python_version)
    with open("pyproject.toml", "w") as f:
        f.write(tomlkit.dumps(doc))


def write_custom_config(user_input_config):
    """Handle custom config overlay."""
    if not user_input_config:
        return

    tmp = TemporaryDirectory()
    tmp_zip = None

    print(user_input_config)

    # if not absolute, test if local path relative to parent of created directory
    if not user_input_config.startswith("/"):
        test_path = Path("..") / user_input_config
    else:
        test_path = Path(user_input_config)

    local_path = None

    # check if user passed a local path
    if test_path.exists() and test_path.is_dir():
        local_path = test_path

    elif test_path.exists() and str(test_path).endswith(".zip"):
        tmp_zip = test_path

    # check if user passed a url to a zip
    elif user_input_config.startswith("http") and (user_input_config.split(".")[-1] in ["zip"]):
        tmp_zip, _ = urlretrieve(user_input_config)

    if tmp_zip:
        with ZipFile(tmp_zip, "r") as zipf:
            zipf.extractall(tmp.name)
            local_path = Path(tmp.name)

    # write whatever the user supplied into the project
    if local_path:
        copytree(local_path, ".", dirs_exist_ok=True)

    tmp.cleanup()


def parse_args():
    parser = argparse.ArgumentParser(description="Post-generation cleanup for Copier template")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--repo-name", required=True)
    parser.add_argument("--env-name", required=True)
    parser.add_argument("--module-name", required=True)
    parser.add_argument("--author-name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--python-version", required=True)
    parser.add_argument("--dataset-storage", required=True)
    parser.add_argument("--s3-bucket", default="")
    parser.add_argument("--s3-aws-profile", default="default")
    parser.add_argument("--azure-container", default="")
    parser.add_argument("--gcs-bucket", default="")
    parser.add_argument("--environment-manager", required=True)
    parser.add_argument("--env-location", default="local")
    parser.add_argument("--dependency-file", required=True)
    parser.add_argument("--pydata-packages", required=True)
    parser.add_argument("--testing-framework", required=True)
    parser.add_argument("--linting-and-formatting", required=True)
    parser.add_argument("--open-source-license", required=True)
    parser.add_argument("--docs", required=True)
    parser.add_argument("--include-code-scaffold", required=True)
    parser.add_argument("--jupyter-kernel-support", required=True)
    parser.add_argument("--env-encryption", required=True)
    parser.add_argument("--docker-support", default="No")
    parser.add_argument("--docker-package-manager", default="uv")
    parser.add_argument("--custom-config", default="")
    return parser.parse_args()


def main():
    args = parse_args()

    # Linting setup
    if args.linting_and_formatting == "ruff":
        # ruff is in dev dependencies, not project dependencies
        # Remove setup.cfg
        Path("setup.cfg").unlink(missing_ok=True)
    # flake8+black+isort are in dev dependencies, not project dependencies

    # Select testing framework
    tests_path = Path("tests")

    if args.testing_framework == "none":
        if tests_path.exists():
            shutil.rmtree(tests_path)
    elif tests_path.exists():
        tests_subpath = tests_path / args.testing_framework
        if tests_subpath.exists():
            # First, collect all items to move
            items_to_move = list(tests_subpath.iterdir())
            for obj in items_to_move:
                dest = tests_path / obj.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(obj), str(tests_path))

        # Remove all remaining tests templates (pytest, unittest directories)
        # Collect first to avoid modifying while iterating
        dirs_to_remove = [d for d in tests_path.iterdir() if d.is_dir()]
        for tests_template in dirs_to_remove:
            shutil.rmtree(tests_template)

    # Use the selected documentation package specified in the config,
    # or none if none selected
    docs_path = Path("docs")
    if docs_path.exists():
        if args.docs != "none":
            docs_subpath = docs_path / args.docs
            if docs_subpath.exists():
                # First, collect all items to move
                items_to_move = list(docs_subpath.iterdir())
                for obj in items_to_move:
                    dest = docs_path / obj.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(obj), str(docs_path))

        # Remove all remaining docs templates (mkdocs directory, etc.)
        # Collect first to avoid modifying while iterating
        dirs_to_remove = [d for d in docs_path.iterdir() if d.is_dir() and d.name != "docs"]
        for docs_template in dirs_to_remove:
            shutil.rmtree(docs_template)

    # environment.yml only kept when dependency_file == "environment.yml" (conda-native dev deps)
    # See docs/docs/env-management.md for the full matrix
    if args.dependency_file != "environment.yml":
        Path("environment.yml").unlink(missing_ok=True)

    # Dependency file handling - see docs/docs/env-management.md for the full matrix
    # - requirements.txt: keep requirements.txt and requirements-dev.txt
    # - pyproject.toml: keep pyproject.toml (with prod+dev deps), delete requirements files
    # - environment.yml: keep environment.yml (dev deps) + pyproject.toml (prod deps), delete requirements files
    if args.dependency_file in ("pyproject.toml", "environment.yml"):
        Path("requirements.txt").unlink(missing_ok=True)
        Path("requirements-dev.txt").unlink(missing_ok=True)
    elif args.dependency_file == "requirements.txt":
        if args.environment_manager == "none":
            # No environment manager means no dev dependencies needed
            Path("requirements-dev.txt").unlink(missing_ok=True)

    write_python_version(args.python_version)

    write_custom_config(args.custom_config)

    # Remove LICENSE if "No license file"
    if args.open_source_license == "No license file":
        Path("LICENSE").unlink(missing_ok=True)

    # Make single quotes prettier
    # Jinja tojson escapes single-quotes with \u0027 since it's meant for HTML/JS
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        pyproject_text = pyproject_path.read_text()
        pyproject_path.write_text(pyproject_text.replace(r"\u0027", "'"))

    if args.include_code_scaffold == "No":
        # remove everything except __init__.py so result is an empty package
        module_path = Path(args.module_name)
        if module_path.exists():
            for generated_path in module_path.iterdir():
                if generated_path.is_dir():
                    shutil.rmtree(generated_path)
                elif generated_path.name != "__init__.py":
                    generated_path.unlink()
                elif generated_path.name == "__init__.py":
                    # remove any content in __init__.py since it won't be available
                    generated_path.write_text("")

    # Remove docker folder when docker support is not selected
    if args.docker_support == "No":
        docker_path = Path("docker")
        if docker_path.exists():
            shutil.rmtree(docker_path)

    # Remove .ipynb_checkpoints if present
    checkpoints_path = Path(".ipynb_checkpoints")
    if checkpoints_path.exists():
        shutil.rmtree(checkpoints_path)

    # Rename .copier-answers.yml.jinja to .copier-answers.yml
    # (needed because _templates_suffix: "" doesn't strip .jinja suffix)
    answers_jinja = Path(".copier-answers.yml.jinja")
    answers_yml = Path(".copier-answers.yml")
    if answers_jinja.exists():
        if answers_yml.exists():
            answers_yml.unlink()
        answers_jinja.rename(answers_yml)

    print("Post-generation cleanup complete!")


if __name__ == "__main__":
    main()
