<!-- Import workspace-level CLAUDE.md configuration -->
<!-- See /home/lab/workspace/.claude/CLAUDE.md for complete rules -->

# Project-Specific Configuration

This file extends workspace-level configuration with project-specific rules.

## Project Context

**Purpose**: Copier-based Data Science template with enhanced features for data science workflows

**Key differentiators from upstream cookiecutter-data-science**:
- Uses Copier (not Cookiecutter) for template updates support
- Local vs global conda environment choice (`env_location`)
- `lib_` module prefix for installable packages
- Rich colored terminal output in Makefile
- environment.yml with pre-configured dev dependencies
- Build and version management targets
- Jupyter kernel auto-registration with nb_venv_kernels/nb_conda_kernels fallback

## Technology Stack

- Copier templating with Jinja2
- Conda/virtualenv/uv environment management
- pytest for testing
- ruff or flake8+black+isort for linting

## Testing

Run tests with parallel execution:
```bash
pytest tests/ -n 4 -v
```

Fast mode for quick iteration:
```bash
pytest tests/ -F
```

### Update Scenario Testing

Testing `copier update` behavior requires git-tracked templates. See [COPIER_UPDATE_TESTING.md](COPIER_UPDATE_TESTING.md) for the tag-based integration testing methodology used for:
- Features that only manifest during update (not fresh copy)
- Conflict resolution testing
- Migration paths from old template versions
