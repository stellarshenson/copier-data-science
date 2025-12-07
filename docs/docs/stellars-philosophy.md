# Stellars' Copier Data Science Philosophy

This fork emphasizes **simplicity**, **separation of concerns**, and **minimal boilerplate**.

## Guiding Philosophy

**Promote best practices, not proliferate outdated ones.**

Project templates shape how thousands of developers work. A project template isn't just scaffolding - it's an opinionated statement about how projects should be structured. We have a responsibility to:

- **Adopt modern tooling** - uv over pip, ruff over flake8+black+isort
- **Deprecate legacy patterns** - Remove virtualenvwrapper, drop pipenv/poetry/pixi complexity
- **Simplify choices** - 3 environment managers instead of 6, focus on what works well
- **Separate dev from production** - clear dependency boundaries
- **Zero post-scaffold configuration** - Jupyter kernels, linting, testing all pre-configured

> [!IMPORTANT]
> Every choice in this template should answer: "Is this how we'd recommend someone start a new project today?"

## Core Principles

### 1. Dev vs Production Dependencies

**Upstream**: All dependencies in one file, no separation.

**This fork**: Strict separation based on dependency file choice:

| Dependency File | Production | Development |
|-----------------|------------|-------------|
| `pyproject.toml` | `[project.dependencies]` | `[project.optional-dependencies.dev]` |
| `requirements.txt` | `requirements.txt` | `requirements-dev.txt` |
| `environment.yml` | conda packages | conda packages (all in one, conda-native) |

> [!TIP]
> This enables lightweight Docker images for production (`pip install .`) while providing full development environment (`pip install -e ".[dev]"`).

### 2. Installable Module with `lib_` Prefix

**Upstream**: Module named `<project_name>` (e.g., `my_project`).

**This fork**: Module named `lib_<project_name>` (e.g., `lib_my_project`).

This avoids conflicts with common package names and makes project code immediately recognizable. A `lib_` prefixed module is far easier to spot in imports than an arbitrary project name - you instantly know it's your local code, not some pip-installed dependency.

> [!NOTE]
> You can rename the module folder to anything you prefer. The `lib_` prefix is just a sensible default that makes your project code easy to spot at a glance.

### 3. Local Environment by Default

**Upstream**: Conda environments always global. Virtualenv uses virtualenvwrapper.

Modern practice is the opposite: one explicit .venv in the project root, tracked in gitignore and documented in `pyproject.toml` or `requirements.txt`. Easier for CI, Docker, editors, teammates.

**This fork**:
- Conda: local `.venv/<env_name>/` by default, global optional
- uv/virtualenv: local `.venv/` using standard venv (no virtualenvwrapper)

> [!WARNING]
> Global conda environments pollute the base environment and can conflict across projects. Local environments provide clear isolation and easy cleanup with `rm -rf .venv`.

### 4. Jupyter Kernel Auto-Registration

**Upstream**: No kernel registration - manual setup required.

**This fork**: Kernels auto-registered during `make create_environment`:
- Uses nb_conda_kernels/nb_venv_kernels when available
- Falls back to ipykernel with consistent naming: `Python [conda|uv|venv env:<name>]`
- Kernels cleaned up on `make remove_environment`

### 5. Environment Existence Checks

**Upstream**: `make create_environment` always tries to create, may fail or recreate.

**This fork**: Checks if environment exists first, skips creation if present.

### 6. Secrets Management with .env Encryption

**Upstream**: No secrets management - `.env` in gitignore, manual handling.

**This fork**: Optional `env_encryption` feature using OpenSSL AES-256:
- `make .env.enc` - encrypts `.env` to `.env.enc` (password-protected)
- `make .env` - decrypts `.env.enc` or creates empty `.env` if no archive exists
- `.env` is dependency of `make install` - auto-decrypts on fresh clone

> [!TIP]
> Commit `.env.enc` to git and share the password out-of-band. On `make install`, team members enter the password once to decrypt secrets.

### 7. Docker Support

**Upstream**: No Docker support.

**This fork**: Optional `docker_support` feature:
- `docker/Dockerfile` - Python slim image, installs from wheel
- `docker/entrypoint.py` - CLI with run/train/predict commands
- `make docker_build` - builds image (depends on `make build`)
- `make docker_run` - runs container with `--rm` flag
- `make docker_push` - tags and pushes to registry

> [!NOTE]
> Docker builds install from wheel (`dist/*.whl`) not source code, ensuring production-like deployment.

## Key Differences from Upstream

| Feature | Upstream ccds | Stellars' Fork |
|---------|--------------|----------------|
| Module naming | `<project_name>` | `lib_<project_name>` |
| Environment managers | 6 (virtualenv, conda, pipenv, uv, pixi, poetry) | 3 (uv, conda, virtualenv) |
| Default env manager | virtualenv | uv |
| Dependency files | 5 (requirements.txt, pyproject.toml, environment.yml, Pipfile, pixi.toml) | 3 (pyproject.toml, requirements.txt, environment.yml) |
| Default Python | 3.10 | 3.12 |
| Conda env location | Global only | Local by default, global optional |
| Dev dependencies | Mixed with production | Separated |
| Jupyter kernel | Manual setup | Auto-registered with cleanup |
| Environment exists check | No | Yes |
| Cloud storage config | Inline in commands | Makefile variables |
| Model sync targets | No | Yes (`sync_models_up/down`) |
| virtualenv implementation | virtualenvwrapper | Standard venv |
| .env encryption | No | Optional (OpenSSL AES-256) |
| Build versioning | No | Auto-increment on `make build` |
| Docker support | No | Optional (Dockerfile + Makefile targets) |
| Template engine | Cookiecutter | Copier (with update support) |

> [!CAUTION]
> This fork intentionally removes support for pipenv, poetry, and pixi. These tools add complexity without proportional benefit for data science workflows. If you need them, use upstream ccds.

## When to Use What

| Scenario | Recommended |
|----------|-------------|
| Data science with conda packages | conda |
| Pure Python, fast setup | uv |
| Traditional Python | virtualenv |

## Acknowledgements

This fork stands on the shoulders of [DrivenData's giants](https://github.com/drivendataorg/cookiecutter-data-science) - peeping over their shoulder at the excellent work they've done, then adding some opinionated tweaks while they do the heavy lifting. All credit for the original architecture goes to the upstream team.
