#!/usr/bin/env python3
"""
Post-generation script for Copier template.

This script performs cleanup and configuration similar to cookiecutter's
hooks/post_gen_project.py but reads configuration from command-line arguments
passed by Copier's _tasks.
"""

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
from zipfile import ZipFile

from jinja2 import Template

# ANSI color codes for migration warnings
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"


def migrate_flat_to_src(module_name):
    """Migrate from flat layout (v1.2.x) to src layout (v1.3.x).

    During copier update, if old flat layout module directory exists at project root,
    move user's code to src/ directory, preserving user modifications over template scaffold.
    """
    old_path = Path(module_name)
    new_path = Path("src") / module_name

    if not old_path.exists() or not old_path.is_dir():
        return  # No old layout to migrate

    if new_path.exists():
        # src/ layout already created by copier template rendering
        # Copy user's files from old location - user's versions take precedence
        for item in old_path.rglob("*"):
            if item.is_file():
                rel = item.relative_to(old_path)
                dest = new_path / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(item), str(dest))
        shutil.rmtree(str(old_path))
    else:
        # src/ doesn't exist yet - just move the directory
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_path), str(new_path))

    # Fix config.py parents depth: parents[1] -> parents[2] for src layout
    config_py = new_path / "config.py"
    if config_py.exists():
        content = config_py.read_text()
        if "parents[1]" in content:
            config_py.write_text(content.replace("parents[1]", "parents[2]"))

    # Print migration warning with ANSI colors
    print(f"\n{BOLD}{CYAN}>>> Migration: {RESET}{module_name}/ -> src/{module_name}/ (src layout)")
    print(f"\n{BOLD}{YELLOW}{'=' * 72}")
    print("  WARNING: Flat -> src layout migration (v1.2.x -> v1.3.x)")
    print(f"{'=' * 72}{RESET}")
    print(f"{YELLOW}  Your module has been moved from:")
    print(f"    {module_name}/  ->  src/{module_name}/")
    print("")
    print("  Please update any hardcoded references to the old path:")
    print("    - Notebook imports using sys.path.append()")
    print(f"    - CI/CD scripts referencing {module_name}/ directly")
    print("    - Custom Makefile targets or shell scripts")
    print("    - Docker COPY instructions for source files")
    print("    - IDE run configurations and debugger paths")
    print("")
    print(f"  Python imports (from {module_name}.xxx import yyy) are NOT affected -")
    print("  the package name is unchanged, only its location on disk moved.")
    print("")
    print(f"  If {module_name}/ still exists at root after update, it may contain")
    print(f"  user-added files preserved by copier. Move them to src/{module_name}/")
    print(f"  and delete the old directory.{RESET}")
    print(f"{BOLD}{YELLOW}{'=' * 72}{RESET}\n")


def resolve_pyproject_conflicts():
    """Resolve conflict markers in pyproject.toml, preserving user changes.

    During `copier update`, if pyproject.toml differs from template, copier adds
    conflict markers like:
        <<<<<<< before updating
        version = "1.2.6"
        =======
        version = "0.1.0"
        >>>>>>> after updating

    This function resolves conflicts by:
    - License-related conflicts: keep user's version (before updating)
    - Version-related conflicts: keep user's version (before updating)
    - Other conflicts: keep template version (after updating)
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return

    content = pyproject_path.read_text()

    # Check if there are conflict markers
    if "<<<<<<< before updating" not in content:
        return

    # Pattern to match conflict blocks
    # Use [\r\n]+ to handle both Unix and Windows line endings
    # and multiple newlines between sections
    conflict_pattern = re.compile(
        r"<<<<<<< before updating[\r\n]+(.*?)[\r\n]+=======[\r\n]+(.*?)[\r\n]+>>>>>>> after updating",
        re.DOTALL,
    )

    def resolve_conflict(match):
        before = match.group(1)  # User's version
        after = match.group(2)  # Template's version

        # Keep user's version for license and version fields
        if "license" in before.lower() or "[project.license]" in before:
            return before
        if "version" in before.lower() and "=" in before:
            return before
        # Otherwise keep template's version
        return after

    resolved = conflict_pattern.sub(resolve_conflict, content)
    pyproject_path.write_text(resolved)


def is_copier_temp_directory():
    """Check if current directory is a copier-created temporary directory.

    During `copier update`, tasks run THREE times:
    1. In temp dir (old template copy for baseline)
    2. In actual project (new template - this is the one we want)
    3. In temp dir (new template copy for diff)

    We only want to run post-generation cleanup for #2.

    Copier creates temp directories with patterns like:
    - /tmp/copier._main.new_copy.XXXXXXXX/ (for update diff)
    - /tmp/copier._vcs.clone.XXXXXXXX/ (for cloning repos)
    """
    cwd = os.getcwd()

    # Match copier's temp directory patterns (not Python's generic tmpXXXXXXXX)
    # Copier uses prefixes like "copier._main.new_copy." or "copier._vcs.clone."
    temp_patterns = [
        r"/tmp/copier\.[^/]+\.[a-z0-9_]+(/|$)",  # Linux: /tmp/copier.xxx.xxx/
        r"/var/folders/.*/T/copier\.[^/]+\.[a-z0-9_]+(/|$)",  # macOS
        r"\\Temp\\copier\.[^\\]+\.[a-z0-9_]+(\\|$)",  # Windows
    ]
    return any(re.search(pattern, cwd, re.IGNORECASE) for pattern in temp_patterns)


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
    """Update requires-python in pyproject.toml using regex (no tomlkit dependency)."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return

    content = pyproject_path.read_text()
    version_spec = resolve_python_version_specifier(python_version)

    # Replace existing requires-python line or add it if missing
    pattern = r'requires-python\s*=\s*"[^"]*"'
    replacement = f'requires-python = "{version_spec}"'

    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
    else:
        # Add requires-python after [project] section
        content = re.sub(
            r"(\[project\][^\[]*?)(name\s*=)",
            rf'\1requires-python = "{version_spec}"\n\2',
            content,
        )

    pyproject_path.write_text(content)


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
    parser.add_argument("--package-repository", default="none")
    parser.add_argument("--package-repository-url", default="")
    parser.add_argument("--custom-config", default="")
    parser.add_argument("--git-init", default="No")
    parser.add_argument("--copier-operation", default="copy")
    parser.add_argument("--ai-assistant", default="none")
    parser.add_argument("--scaffold-agents", default="No")
    parser.add_argument("--github-actions", default="No")
    return parser.parse_args()


def main():
    # Skip execution in temp directories - copier update runs tasks there too
    # We only want to run for the actual project directory copy
    if is_copier_temp_directory():
        return

    _do_post_gen()


def is_copier_update(copier_operation):
    """Check if this is a copier update (vs fresh copy).

    Copier exposes the operation it is running as `_copier_operation` ("copy" or
    "update", added in copier 9.6.0); copier.yml passes it through as --copier-operation
    and pins _min_copier_version accordingly.

    There is deliberately no fallback heuristic. The obvious one - sniffing
    .copier-answers.yml for a _commit field - is wrong whenever the template is copied
    from a VCS ref, because copier records _commit on a fresh copy too, so it reports
    every fresh copy as an update.

    Note `copier recopy` reports "copy", not "update", so anything gated on this must
    stay safe for a run over a directory that already holds the user's files.
    """
    return copier_operation == "update"


def is_same_text(left, right):
    """Compare two file bodies, ignoring a difference in the trailing newline.

    Jinja's Template() drops the final newline while copier keeps it, so a byte
    comparison between a re-render and the file copier wrote never matches.
    """
    if left is None or right is None:
        return False
    return left.rstrip("\n") == right.rstrip("\n")


def is_untouched_instructions(text, variants):
    """Check whether an instructions file is still exactly what the template produced.

    The heading follows the selected assistant, so a file written for a different
    assistant is compared against that assistant's variant too - otherwise a
    switched-away copy would look user-edited and never be cleaned up.
    """
    return any(is_same_text(text, variant) for variant in variants)


def is_template_owned_dir(path):
    """Check whether a directory holds nothing but the .gitkeep this script writes.

    Gates the recursive deletes below: a folder the user has put real content into is
    never removed, however the corresponding question was answered.
    """
    if not path.is_dir():
        return False
    return {child.name for child in path.iterdir()} <= {".gitkeep"}


def _do_post_gen():
    """Actual post-generation logic."""
    args = parse_args()

    # Resolve any conflict markers in pyproject.toml (preserves custom license)
    resolve_pyproject_conflicts()

    is_update = is_copier_update(args.copier_operation)

    # Migrate flat layout to src layout during copier update (v1.2.x -> v1.3.x)
    if is_update:
        migrate_flat_to_src(args.module_name)

    # Linting setup
    if args.linting_and_formatting == "ruff":
        # ruff is in dev dependencies, not project dependencies
        # Remove setup.cfg
        Path("setup.cfg").unlink(missing_ok=True)
    # flake8+black+isort are in dev dependencies, not project dependencies

    # Select testing framework
    tests_path = Path("tests")

    if args.testing_framework == "none":
        # Delete entire tests folder when testing is disabled
        if tests_path.exists():
            shutil.rmtree(tests_path)
    elif args.testing_framework in ("pytest", "unittest"):
        # Ensure tests folder exists with properly rendered templates
        # During update from testing_framework=none, folder won't exist - need to create it
        template_tests = (
            Path(__file__).parent.parent / "template" / "tests" / args.testing_framework
        )
        if template_tests.exists():
            tests_path.mkdir(parents=True, exist_ok=True)
            # Template context for rendering test files
            context = {
                "module_name": args.module_name,
                "project_name": args.project_name,
                "repo_name": args.repo_name,
            }
            for template_file in template_tests.iterdir():
                if template_file.is_file():
                    dest = tests_path / template_file.name
                    # During update, don't overwrite user's existing test files
                    if not (is_update and dest.exists()):
                        content = template_file.read_text()
                        rendered = Template(content).render(**context)
                        dest.write_text(rendered)

        # Remove template directories (pytest, unittest) if they still exist
        template_test_dirs = ["pytest", "unittest"]
        for template_dir in template_test_dirs:
            template_path = tests_path / template_dir
            if template_path.exists():
                shutil.rmtree(template_path)

    # Use the selected documentation package specified in the config
    docs_path = Path("docs")
    if docs_path.exists():
        if args.docs != "none":
            docs_subpath = docs_path / args.docs
            if docs_subpath.exists():
                # Move template files to docs/ root
                # Fresh copy: overwrite (user hasn't modified yet)
                # Update: only move if dest doesn't exist (preserve user's files)
                items_to_move = list(docs_subpath.iterdir())
                for obj in items_to_move:
                    dest = docs_path / obj.name
                    if is_update and dest.exists():
                        # During update, don't overwrite user's files
                        pass
                    else:
                        # Fresh copy or dest doesn't exist
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(obj), str(docs_path))

        # Always remove template directories (mkdocs)
        template_doc_dirs = ["mkdocs"]
        for template_dir in template_doc_dirs:
            template_path = docs_path / template_dir
            if template_path.exists():
                shutil.rmtree(template_path)

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
        module_path = Path("src") / args.module_name
        if module_path.exists():
            for generated_path in module_path.iterdir():
                if generated_path.is_dir():
                    shutil.rmtree(generated_path)
                elif generated_path.name != "__init__.py":
                    generated_path.unlink()
                elif generated_path.name == "__init__.py":
                    # remove any content in __init__.py since it won't be available
                    generated_path.write_text("")

    # Handle docker folder based on docker_support setting
    docker_path = Path("docker")
    if args.docker_support == "No":
        # Remove docker folder when docker support is not selected
        if docker_path.exists():
            shutil.rmtree(docker_path)
    elif args.docker_support == "Yes":
        # Ensure docker folder exists with properly rendered templates
        # During update, copier may create it but then remove it (since it wasn't in original)
        # We need to render templates ourselves to ensure they're correct
        template_docker = Path(__file__).parent.parent / "template" / "docker"
        if template_docker.exists():
            docker_path.mkdir(parents=True, exist_ok=True)
            # Template context for rendering docker files
            context = {
                "module_name": args.module_name,
                "python_version_number": args.python_version,
                "docker_package_manager": args.docker_package_manager,
                "project_name": args.project_name,
                "description": args.description,
            }
            for template_file in template_docker.iterdir():
                if template_file.is_file():
                    content = template_file.read_text()
                    rendered = Template(content).render(**context)
                    (docker_path / template_file.name).write_text(rendered)

    # Handle the AI assistant instructions file and internal resources folder.
    # Each assistant reads its project instructions from a different path: Claude Code
    # reads .claude/CLAUDE.md, Gemini CLI reads GEMINI.md at the project root, and Codex
    # and the generic AGENTS.md standard read AGENTS.md at the project root. The
    # dot-folder is the home for that assistant's project-internal resources.
    ai_assistant_layout = {
        "claude": (Path(".claude") / "CLAUDE.md", Path(".claude")),
        "codex": (Path("AGENTS.md"), Path(".codex")),
        "gemini": (Path("GEMINI.md"), Path(".gemini")),
        "generic": (Path("AGENTS.md"), Path(".agents")),
    }
    # The template ships the instructions as CLAUDE.md at the project root
    claude_md_path = Path("CLAUDE.md")

    # Rendering the template up front lets us tell an untouched copy of the instructions
    # apart from one the user has edited, so we never delete their work
    template_claude = Path(__file__).parent.parent / "template" / "CLAUDE.md"
    rendered_instructions = None
    untouched_variants = []
    if template_claude.exists():
        instructions_template = Template(template_claude.read_text(), keep_trailing_newline=True)
        instructions_context = {
            "module_name": args.module_name,
            "python_version_number": args.python_version,
            "environment_manager": args.environment_manager,
            "env_location": args.env_location,
            "env_name": args.env_name,
            "include_code_scaffold": args.include_code_scaffold,
            "dataset_storage": args.dataset_storage,
            "docs": args.docs,
            "package_repository": args.package_repository,
            "docker_support": args.docker_support,
            "jupyter_kernel_support": args.jupyter_kernel_support,
            "scaffold_agents": args.scaffold_agents,
        }
        rendered_instructions = instructions_template.render(
            ai_assistant=args.ai_assistant, **instructions_context
        )
        # One variant per assistant: a copy written for the assistant being switched away
        # from is still template output, and must be recognised as such to be cleaned up
        untouched_variants = [
            instructions_template.render(ai_assistant=name, **instructions_context)
            for name in ("none", "claude", "codex", "gemini", "generic")
        ]

    # Where an existing instructions file may be found, most specific first - the template
    # drops its copy at the project root, so that one is the last resort
    known_instructions = []
    for path, _ in ai_assistant_layout.values():
        if path not in known_instructions:
            known_instructions.append(path)
    known_instructions.append(claude_md_path)

    layout = ai_assistant_layout.get(args.ai_assistant)
    if layout is None:
        # "none" - drop every untouched copy the template produced, whichever assistant it
        # was written for, so a switched-away tool stops being read. The content check is
        # the only gate: a copy into a directory that already holds a hand-written
        # instructions file (copier copy --overwrite, or copier recopy, both of which
        # report the operation as "copy") must not delete the user's work.
        for stale in known_instructions:
            if stale.exists() and is_untouched_instructions(stale.read_text(), untouched_variants):
                stale.unlink()
    else:
        instructions_path, internal_dir = layout
        source = None
        # Write the instructions file if missing (a fresh copy has it at the root; this
        # covers enabling during update where copier removes files not in the original).
        # Write-if-missing preserves user edits on subsequent updates.
        if not instructions_path.exists():
            # Carry an existing file over so switching assistant keeps the user's edits.
            # Only an update is a switch - on a copy there is no previous answer to switch
            # from, so only the template's own root drop may be moved into place.
            candidates = known_instructions if is_update else [claude_md_path]
            source = next(
                (p for p in candidates if p != instructions_path and p.exists()),
                None,
            )
            content = source.read_text() if source else rendered_instructions
            if content is not None:
                instructions_path.parent.mkdir(parents=True, exist_ok=True)
                instructions_path.write_text(content)
        # Drop the other layouts' copies so a switched-away assistant stops being read.
        # Only the file just carried over to the new location and untouched template
        # output are removed, so edits are never destroyed - but note a file the user
        # wrote for another tool is carried over rather than left where it was, since
        # that is indistinguishable from a genuine switch.
        for stale in known_instructions:
            if stale == instructions_path or not stale.exists():
                continue
            if stale == source or is_untouched_instructions(stale.read_text(), untouched_variants):
                stale.unlink()
        # Keep the internal folder tracked when the instructions file lives outside it
        internal_dir.mkdir(parents=True, exist_ok=True)
        if not any(internal_dir.iterdir()):
            (internal_dir / ".gitkeep").write_text("")

    # Remove the internal folders of the assistants that were not selected, so switching
    # assistant during an update does not leave the previous one behind. Only a folder
    # holding nothing but our own .gitkeep goes - user content is never touched.
    for _, unused_dir in ai_assistant_layout.values():
        if layout is not None and unused_dir == layout[1]:
            continue
        if is_template_owned_dir(unused_dir):
            shutil.rmtree(unused_dir)

    # Handle agents/ folder based on scaffold_agents setting
    # Holds deployable agentic resources (workflows, exported skills); only a .gitkeep is
    # scaffolded since the internal structure depends on the framework the user adopts.
    agents_path = Path("agents")
    if args.scaffold_agents == "No":
        # Only the folder the template created is removed - a user's own agents/ content
        # survives, including when an older project takes this question's default of No
        if is_template_owned_dir(agents_path):
            shutil.rmtree(agents_path)
        else:
            # The template always renders agents/.gitkeep, so drop that marker when a
            # user-owned agents/ is being kept - otherwise it reappears on every update
            (agents_path / ".gitkeep").unlink(missing_ok=True)
    elif args.scaffold_agents == "Yes":
        # Ensure agents/.gitkeep exists (covers enabling during update where copier
        # removes files not present in the original project)
        if not agents_path.exists():
            agents_path.mkdir(parents=True, exist_ok=True)
            (agents_path / ".gitkeep").write_text("")

    # Handle .github folder based on github_actions setting
    github_path = Path(".github")
    if args.github_actions == "No":
        if github_path.exists():
            shutil.rmtree(github_path)
    elif args.github_actions == "Yes":
        # Render workflow if missing (covers enabling during update where copier
        # strips files absent from the original project); preserves user edits otherwise
        workflow_path = github_path / "workflows" / "tests.yml"
        if not workflow_path.exists():
            template_workflow = (
                Path(__file__).parent.parent / "template" / ".github" / "workflows" / "tests.yml"
            )
            if template_workflow.exists():
                workflow_path.parent.mkdir(parents=True, exist_ok=True)
                context = {
                    "environment_manager": args.environment_manager,
                    "python_version_number": args.python_version,
                    "testing_framework": args.testing_framework,
                    "env_encryption": args.env_encryption,
                }
                rendered = Template(template_workflow.read_text()).render(**context)
                workflow_path.write_text(rendered)

    # Remove .ipynb_checkpoints if present
    checkpoints_path = Path(".ipynb_checkpoints")
    if checkpoints_path.exists():
        shutil.rmtree(checkpoints_path)

    # .copier-answers.yml is now managed entirely by copier itself
    # We don't touch it in post_gen to avoid conflicts

    # Initialize git repository if requested and not already initialized
    if args.git_init == "Yes" and not Path(".git").exists():
        subprocess.run(["git", "init", "-b", "main"], check=True)

    print("Post-generation cleanup complete!")


if __name__ == "__main__":
    main()
