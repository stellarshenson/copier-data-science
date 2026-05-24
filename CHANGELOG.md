# Changelog

## v1.3.9 (2026-05-25) - Python version choices

- Changed default Python to 3.13
- `python_version` is now a choice prompt - `3.12`, `3.13`, `3.14`, or `other`
- Selecting `other` opens a follow-up prompt to type any version (e.g. `3.10`)
- Downstream templates unchanged - the computed `python_version_number` still drives Makefile, pyproject.toml, environment.yml, and Dockerfile

## v1.3.8 (2026-05-20) - Auto-bump on install + README feature refresh

- Standardized version-increment behavior across env managers - `make install` now increments the patch version for virtualenv, uv, and conda (previously only virtualenv)
- Removed duplicate increment from uv and conda `build` targets (would have double-bumped since `build` depends on `install`)
- Added `SKIP_VERSION_INCREMENT` Makefile variable - set to `1` to skip the auto-bump during repeated dev installs
- Refreshed root `README.md` Key Features table and bullet list to reflect current state (src layout, sync exclusions, .env tier ignores, install-time versioning, optional git init); removed stale `lib_` default messaging

## v1.3.7 (2026-05-20) - Restore changelog maintenance

- Restored CHANGELOG.md maintenance after long gap (last entry was v1.0.61, December 2025)
- Backfilled entries for v1.3.5 and v1.3.6
- Going forward, every release bump includes a CHANGELOG entry

## v1.3.6 (2026-05-20) - .gitignore env tiers and nodeenv

- Added `.env.dev`, `.env.prod`, `.env.stg`, `.env.test` to template `.gitignore` to prevent leaking per-tier secrets
- Added `.nodeenv` to template `.gitignore` for Python/Node mixed projects

## v1.3.5 (2026-05-20) - Sync exclusion fixes

- Excluded `.gitkeep`, `.gitattributes`, `.gitignore` from `sync_data_*` and `sync_models_*` targets across AWS S3, Azure, GCS
- Fixed `.ipynb_checkpoints` exclusion pattern - `*/.ipynb_checkpoints/*` missed root-level checkpoint dirs (e.g. `models/.ipynb_checkpoints/`); changed to `*.ipynb_checkpoints/*` for S3 and Azure (GCS regex already correct)

## v1.0.61 (2025-12-07) - Copier-Only Migration

Major migration from dual cookiecutter/copier template to copier-only project.

**Breaking Changes:**
- Removed all cookiecutter infrastructure - this is now a copier-only template
- Changed repository to `stellarshenson/copier-data-science`
- Version scheme changed from `2.3.0+stellarsNN` to `1.0.NN`

**Changes:**
- Moved template from `copier/template/` to `template/`
- Removed: `ccds/` module, `ccds.json`, `cookiecutter.json`, `hooks/`, `{{ cookiecutter.repo_name }}/`
- Updated `copier.yml` with `_subdirectory: template`
- Simplified test suite (removed cookiecutter tests)
- Updated CI workflows to use copier
- Consolidated dev dependencies to `pyproject.toml`

## v2.3.0+stellars60 (2025-12-06) - Template Sync & Docker Tests

- Added template sync test to verify copier template stays in sync with cookiecutter
- Added Docker tests for uv and pip package managers
- Fixed PEP 639 license format (SPDX identifiers)
- Simplified generated project README

## v2.3.0+stellars50 (2025-12-05) - Docker Support

- Added optional Docker support (`docker_support` option)
- Dockerfile with uv or pip package manager choice
- Makefile targets: `docker_build`, `docker_run`, `docker_push`
- Python version configurable via build arg

## v2.3.0+stellars46 (2025-12-04) - Copier GitHub URL Support

- Moved `copier.yml` to repo root for direct GitHub URL usage
- Auto-derive `project_name` from destination folder
- Added `.env` encryption option (OpenSSL AES-256)

## v2.3.0+stellars42 (2025-12-03) - Copier Implementation

- Added Copier template support alongside Cookiecutter
- Build script transforms cookiecutter syntax to copier
- Both tools produce identical project output
- Template updates via `copier update`

## v2.3.0+stellars35 (2025-12-02) - Environment Improvements

- Added `sync_models_up/down` Makefile targets
- Unified `ENV_NAME` variable across all managers
- Consistent Jupyter kernel naming
- Cloud storage variables in Makefile

## v2.3.0+stellars28 (2025-12-01) - Test Matrix & Env Management

- Created `env_matrix.py` as single source of truth for file expectations
- Added `environment.yml` as dependency file option for conda
- Template-based dependency management (removed dynamic generation)
- Standardized dev dependency handling

## v2.3.0+stellars21 (2025-11-30) - ccds v2 Port

Initial port of Stellars fork features to ccds v2:

- Local/global conda environment choice (`env_location`)
- `lib_` module prefix for installable packages
- uv as default environment manager
- Colored Makefile output
- Jupyter kernel auto-registration
- Dev/prod dependency separation
- Build versioning (`make build` increments version)

---

## Upstream History (DrivenData cookiecutter-data-science)

### v2.3.0 (2025-07-23)
- Added `pixi` as environment manager option
- Added `poetry` as environment manager option

### v2.2.0 (2025-03-23)
- Added `pyproject.toml` as dependencies file format
- Added test scaffolding choice (pytest/unittest)

### v2.1.0 (2025-03-10)
- Added Ruff as linting option (now default)
- Added `uv pip` as environment manager option

### v2.0.0 (2024-05-22)
- Major version 2 release with new architecture
