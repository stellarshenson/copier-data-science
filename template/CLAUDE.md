# Project Configuration for Claude Code

Guidance for Claude Code and other AI assistants working in this repository.

## Project Context

- **Module**: `src/{{ module_name }}/` - importable package (`import {{ module_name }}`)
- **Python**: {{ python_version_number }}
- **Environment manager**: {{ environment_manager }}
{%- if environment_manager == 'conda' and (env_location | default('local')) == 'global' %}
- **Environment**: conda environment `{{ env_name }}` (global)
{%- else %}
- **Environment**: `.venv/` in the project root
{%- endif %}

## Make Commands

This project is driven by a self-documenting Makefile. Run `make help` at any time to list every available target with its description - it is always the authoritative, up-to-date reference.

Common targets:

```
make help                 # list all available commands
make create_environment   # create the {{ environment_manager }} environment
make install              # install the package in editable mode (bumps patch version)
make requirements         # install or refresh dependencies
make test                 # run the test suite
make lint                 # check formatting and lint
make format               # auto-format the source
make clean                # remove compiled Python artifacts
{%- if include_code_scaffold == 'Yes' %}
make data                 # run the dataset pipeline
{%- endif %}
{%- if dataset_storage in ['s3', 'azure', 'gcs'] %}
make sync_data_up         # upload data/ to cloud storage
make sync_data_down       # download data/ from cloud storage
make sync_models_up       # upload models/ to cloud storage
make sync_models_down     # download models/ from cloud storage
{%- endif %}
{%- if docs == 'mkdocs' %}
make docs                 # build the documentation
make docs_serve           # serve the documentation locally
{%- endif %}
make build                # build the wheel package
{%- if package_repository == 'Yes' %}
make publish              # publish the package to the configured repository
{%- endif %}
{%- if docker_support == 'Yes' %}
make docker_build         # build the Docker image
make docker_run           # run the Docker container
make docker_push          # push the image to the registry
{%- endif %}
```

Set `SKIP_VERSION_INCREMENT=1` (e.g. `make install SKIP_VERSION_INCREMENT=1`) to skip the automatic patch bump during iterative development.

## Engineering Principles

- **Think before coding** - state assumptions, surface trade-offs, and ask when the request is ambiguous rather than guessing
- **Simplicity first** - write the minimum code that solves the problem; no speculative abstractions or unrequested configurability
- **Surgical changes** - touch only what the task requires, match the surrounding style, and do not refactor unrelated code
- **Verify** - turn tasks into checks (write a failing test, then make it pass) and confirm before declaring done

## Data Science Conventions

- **Notebooks** - in `notebooks/`, numbered (`1.0-initial-exploration.ipynb`); import from `src/{{ module_name }}/` instead of redefining code in cells; keep only exploratory or one-off code here
- **Refactor** stable notebook and experiment code into `src/{{ module_name }}/`
- **Experiments** - code and harnesses in `src/experiments/` (create as needed; source-only, not shipped); results in `reports/experiments/`; papers and digests in `references/papers/`; graduate stable code into the module
- **Scripts** - no root `scripts/`; use `src/experiments/`
- **Data** - not committed by default (tree and Markdown tracked, data files ignored); only small (~50 MB), processed, non-reproducible data may be committed. Every data folder keeps a `README.md` index; every large file (dump, parquet) gets a `<file>.md` sidecar. DB dumps go under `data/external/dumps/` (raw) or `data/interim/dumps/` (processed), created as needed. See `data/README.md`
- **Models** - only lightweight self-developed or fine-tuned models (~100 MB, case by case), in purpose-named folders (`embedders/`, `classifiers/`), each with a `.md` sidecar; never commit third-party models (Hugging Face) - use model sync (S3). See `models/README.md`
- **Logs** - `logs/` holds runtime and job logs (gitignored); `... 2>&1 | tee logs/<name>.log`, with a short `logs/README.md`
- **Temporary files** - `tmp/` is gitignored throwaway scratch (subfolders like `tmp/scripts/`, `tmp/data/` are fine); never keep anything here
{%- if scaffold_ai == 'Yes' %}
- **Agentic resources** - `ai/` holds agentic framework and harness resources (skills, hooks, workflow files); its internal layout follows whatever framework the project adopts
{%- endif %}
{%- if jupyter_kernel_support == 'Yes' %}
- **Jupyter kernel** is auto-registered as `{{ env_name }}`; re-register with `make register_environment` if it goes missing
{%- endif %}

## Conventions

- No emojis in code or documentation; keep a professional, technical tone
- Prefer clear names and short functions over clever one-liners
- Keep secrets in `.env` (gitignored); never commit credentials
