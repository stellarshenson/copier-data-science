# {{ project_name }}

{{ description }}

> **Note**: Generated with copier-data-science template v1.2+
> For template documentation, visit [copier-data-science](https://github.com/stellarshenson/copier-data-science)

## Quick Start

```bash
make install
```

## Makefile Targets

- `make install` - Create environment and install package
- `make test` - Run tests
- `make lint` / `make format` - Check / fix code style
- `make data` - Run the dataset pipeline (`src/{{ module_name }}/dataset.py`)
- `make upgrade` - Upgrade dependencies to latest versions
- `make build` - Build distributable wheel
- `make clean` - Remove compiled files, caches, logs and tmp
{%- if docs == 'mkdocs' %}
- `make docs` / `make docs_serve` - Build / serve documentation
{%- endif %}
{%- if dataset_storage in ['s3', 'azure', 'gcs'] %}
- `make sync_data_down` / `make sync_data_up` - Sync data with cloud storage
- `make sync_models_down` / `make sync_models_up` - Sync models with cloud storage
{%- endif %}
{%- if docker_support == 'Yes' %}
- `make docker_build` / `make docker_run` - Build and run Docker container
{%- endif %}
{%- if env_encryption == 'Yes' %}
- `make .env` / `make .env.enc` - Decrypt / encrypt environment secrets
{%- endif %}
- `make help` - Show all available targets

## Best Practices

- **Notebooks**: organized in task-specific folders (`exploration/`, `training/`, `evaluation/`) rather than a flat list, numbered in execution order inside each (`01-data-exploration.ipynb`); import from `src/{{ module_name }}/` instead of redefining code in cells; keep only exploratory or one-off code here. See [notebooks/README.md](notebooks/README.md)
- **Source code**: graduate stable notebook and experiment code into `src/{{ module_name }}/`
- **Experiments**: experiment code and scripts in `src/experiments/` (created as needed, source-only, not shipped, safe to delete) - keeps scripts in one place instead of scattered across the project, so experiment notebooks in `notebooks/experiments/` can import unified, shared code from it; results in `reports/experiments/`, experiment data in `data/experiments/`; papers and digests in `references/papers/`
- **Data**: not committed by default; only small (~50 MB), processed, non-reproducible data belongs in git. Every data folder keeps a `README.md` index; every large file (dump, parquet) gets a `<name>.md` sidecar named without the original extension (`sales.parquet` → `sales.md`, not `sales.parquet.md`). DB dumps go under `data/external/dumps/` (raw) or `data/interim/dumps/` (processed), created as needed. See [data/README.md](data/README.md)
- **Models**: only lightweight self-developed or fine-tuned models (~100 MB, case by case) in purpose-named folders (`embedders/`, `classifiers/`), each with a `.md` sidecar; never commit third-party models (Hugging Face) - use model sync (S3). See [models/README.md](models/README.md)
- **Documentation**: `docs/` holds the project's own documentation - dataset and model recipes, exploration and scientific method walkthrough, experiments, SOTA solution, acceptance criteria, defects. See [docs/README.md](docs/README.md)
- **References**: `references/` holds material brought in from outside the project - data descriptions and dictionaries, papers and digests in `references/papers/`, manuals and API docs. See [references/README.md](references/README.md)
- **Logs**: runtime and job logs in `logs/` (gitignored), with a short `logs/README.md`
- **Temporary files**: `tmp/` for throwaway work (gitignored); never keep anything here

## Project Organization

```
├── Makefile           <- Makefile with convenience commands
├── README.md          <- The top-level README for developers
{%- if ai_assistant == 'claude' %}
├── .claude            <- Project instructions (CLAUDE.md) and internal assistant resources
{%- elif ai_assistant == 'codex' %}
├── AGENTS.md          <- Project instructions for Codex
├── .codex             <- Internal assistant resources
{%- elif ai_assistant == 'gemini' %}
├── GEMINI.md          <- Project instructions for Gemini CLI
├── .gemini            <- Internal assistant resources
{%- elif ai_assistant == 'generic' %}
├── AGENTS.md          <- Project instructions (AGENTS.md standard)
├── .agents            <- Internal assistant resources
{%- endif %}
{%- if scaffold_agents == 'Yes' %}
├── agents             <- Deployable agentic resources (workflows, exported skills)
{%- endif %}
├── data               <- Each folder keeps a README.md index; large files get a .md sidecar
│   ├── external       <- Data from third party sources
│   ├── interim        <- Intermediate data that has been transformed
│   ├── processed      <- The final, canonical data sets for modeling
│   └── raw            <- The original, immutable data dump
│
├── docs               <- Project documentation: recipes, experiments, SOTA, acceptance criteria{% if docs != 'none' %} ({{ docs }}){% endif %}
{%- if docker_support == 'Yes' %}
├── docker             <- Docker configuration
{%- endif %}
├── logs               <- Runtime and background-job logs (gitignored)
├── models             <- Trained and serialized models
├── notebooks          <- Jupyter notebooks, organized in task-specific folders
├── tmp                <- Throwaway scratch: temp scripts, notebooks, data (gitignored)
├── pyproject.toml     <- Project configuration and dependencies
├── references         <- External material: data descriptions, papers, manuals
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures
{%- if dependency_file == 'requirements.txt' %}
├── requirements.txt   <- Runtime dependencies
├── requirements-dev.txt <- Development dependencies
{%- elif dependency_file == 'environment.yml' %}
├── environment.yml    <- Conda environment with all dependencies
{%- endif %}
├── tests              <- Test files
└── src
    └── {{ module_name }}   <- Source code for this project
        ├── __init__.py
        ├── config.py      <- Configuration variables
        ├── dataset.py     <- Data download/generation scripts
        ├── features.py    <- Feature engineering code
        ├── modeling
        │   ├── predict.py <- Model inference
        │   └── train.py   <- Model training
        └── plots.py       <- Visualization code
```
