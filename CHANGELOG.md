# Changelog

## v1.3.13 (2026-07-13) - Experiment and data-layout conventions

- Documented how experiments and data are organized in a generated project
- `src/experiments/` is a Python module for experiment code and scripts - source-only, not shipped in the wheel, and safe to delete; keeps scripts in one place instead of scattered across the project
- Experiment notebooks go in `notebooks/experiments/` and can import shared code from `src/experiments/`; results in `reports/experiments/`, experiment data in `data/experiments/`, kept papers and digests in `references/papers/` (all created as needed)
- Data: rewrote the `.gitignore` data block to a single `/data/**` pattern that keeps the folder tree and all Markdown (README indexes + file sidecars) while ignoring data files; each data folder now carries a `README.md` index and every large file (dump, parquet) takes a `<file>.md` sidecar
- DB dumps go under `data/external/dumps/` (raw) or `data/interim/dumps/` (processed), created as needed
- `_skip_if_exists` uses `data/**/README.md` so user-maintained data indexes survive `copier update`

## v1.3.12 (2026-07-11) - Data and model repository-inclusion rules

- Documented the policy for what data and models belong in a generated project's git repo
- Data: not committed by default; only small (~50 MB) processed, non-reproducible data may be committed - external and large data stays in cloud storage with a `README` or `.md` sidecar recording provenance and location for re-download
- Models: commit only lightweight self-developed or fine-tuned models (~100 MB, case by case) in purpose-named folders (`embedders/`, `classifiers/`, ...) each with a brief `.md` sidecar; standard third-party models (e.g. Hugging Face) are never committed and move through model sync (S3)
- New `data/README.md` and `models/README.md` in the generated project; rules also summarized in the project `README.md` and (when enabled) `CLAUDE.md`
- Added `!/data/README.md` to the generated `.gitignore` so the data README is trackable; both READMEs added to `_skip_if_exists` so user-authored provenance survives `copier update`

## v1.3.11 (2026-07-08) - Makefile env-context fixes and GitHub Actions CI

- Fixed `make data` running bare `python` for uv/virtualenv - now uses the project `.venv/bin/python`
- Fixed the virtualenv `requirements` target escaping the venv with bare `pip` - now uses `.venv/bin/pip` and installs dev dependencies (matching conda)
- Fixed flake8+black+isort `lint`/`format` running outside the environment context - now branched per environment manager like ruff
- Bare `make` now prints help (`.DEFAULT_GOAL := help`)
- `make clean` now removes `logs/` and `tmp/`
- New `github_actions` option (default No) - scaffolds `.github/workflows/tests.yml` matched to the environment manager (setup-uv / miniconda / setup-python), running `make install`, `lint`, and `test`
- Added `[tool.pytest.ini_options] testpaths` to the generated `pyproject.toml`; completed `.PHONY`; refreshed README target lists and feature table

## v1.3.10 (2026-07-08) - Agentic scaffolding and logs/tmp ignores

- Added `logs/` and `tmp/` to the generated project `.gitignore` - `logs/` for runtime and background-job output, `tmp/` for temporary artefacts
- New `claude_md` option (default No) - scaffolds a `CLAUDE.md` with project context, engineering principles, and a make-command reference (`make help`)
- New `scaffold_ai` option (default No) - scaffolds an `ai/` folder (single `.gitkeep`) for agentic framework and harness resources; internal layout left to the framework
- Documented `logs/`, `tmp/`, and `ai/` in the generated README and CLAUDE.md

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
