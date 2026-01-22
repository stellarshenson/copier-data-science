# Copier Update Testing

This document describes the methodology for testing `copier update` scenarios that require git-tracked templates.

## The Problem

Copier's `update` command only works with git-tracked templates. Running `copier update` on a project created from a local path fails with:

```
Updating is only supported in git-tracked templates
```

This creates a challenge for testing update scenarios like:
- Enabling a feature during update that was disabled during creation
- Preserving user changes during update
- Testing conflict resolution

## Solution: Tag-Based Integration Tests

For features that depend on copier update behavior, we use **tag-based integration tests** that run against actual GitHub releases.

### Test Flow

1. Create project using `copier copy --vcs-ref <old-tag>` from GitHub URL
2. Initialize git in the project (`git init && git add -A && git commit`)
3. Run `copier update --vcs-ref <new-tag>` to simulate update
4. Verify expected changes were applied

### Example: Docker Update Scenario

```python
import subprocess
import tempfile

def test_docker_enabled_during_update():
    """Test enabling docker_support during copier update."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = f"{tmp}/test-project"

        # Step 1: Create project at old version without docker
        subprocess.run([
            "copier", "copy", "--trust", "--defaults",
            "--vcs-ref", "v1.2.15",
            "-d", "docker_support=No",
            "https://github.com/stellarshenson/copier-data-science.git",
            project_path
        ], check=True)

        # Step 2: Initialize git (required for update)
        subprocess.run(["git", "init"], cwd=project_path, check=True)
        subprocess.run(["git", "add", "-A"], cwd=project_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=project_path, check=True)

        # Verify no docker folder initially
        assert not (Path(project_path) / "docker").exists()

        # Step 3: Update to newer version with docker enabled
        subprocess.run([
            "copier", "update", "--trust", "--defaults",
            "--vcs-ref", "v1.2.18",
            "-d", "docker_support=Yes",
        ], cwd=project_path, check=True)

        # Step 4: Verify docker folder was created
        docker_dir = Path(project_path) / "docker"
        assert docker_dir.exists(), "docker/ should exist after update"
        assert (docker_dir / "Dockerfile").exists()
        assert (docker_dir / "entrypoint.py").exists()
```

### When to Use This Pattern

Use tag-based integration tests when testing:
- **Update-specific behavior**: Features that only manifest during update, not fresh copy
- **Conflict resolution**: How pyproject.toml or other files handle conflicts
- **Migration paths**: Upgrading from old template versions
- **Answer file handling**: Verifying `_commit` and other fields update correctly

### When NOT to Use This Pattern

For features that can be tested with fresh copies, use the standard `bake_project()` helper from `conftest.py`. This is faster and doesn't require network access.

### Test Markers

Mark these tests appropriately so they can be skipped in CI if needed:

```python
@pytest.mark.integration
@pytest.mark.requires_network
def test_update_scenario():
    ...
```

## Key Insights

### Copier Update Removes New Directories

During `copier update`, copier computes a diff between old and new template versions. Files/directories that exist in the new template but weren't in the original project may be:

1. Created during template rendering
2. Removed after task execution if they don't match the original project state

**Solution**: Use `_skip_if_exists` in `copier.yml` to preserve directories created by `_tasks`:

```yaml
_skip_if_exists:
  - docker/
```

Combined with post_gen.py logic that always creates the directory when enabled:

```python
elif args.docker_support == "Yes":
    # Always ensure docker folder exists with rendered templates
    docker_path.mkdir(parents=True, exist_ok=True)
    # ... render templates ...
```

### Task Execution Order

Tasks run DURING copier's processing, not after. Specifically:

1. Copier renders templates to project directory
2. Tasks execute (post_gen.py runs)
3. Copier may apply additional cleanup/conflict resolution

This means tasks see intermediate state, not final state. The `_skip_if_exists` directive prevents copier from overwriting or removing files created by tasks.

## Related Files

- `tests/test_docker.py` - Contains `TestDockerUpdateScenario` class
- `scripts/post_gen.py` - Post-generation cleanup and docker folder creation
- `copier.yml` - Template configuration including `_skip_if_exists`
