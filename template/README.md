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

- **Notebooks**: Name with number prefix, initials, description - `01-jqp-data-exploration.ipynb`
- **Data**: Keep `raw/` immutable, `interim/` for transforms, `processed/` for final datasets. Do not commit data by default - only small (about 50 MB), processed, non-reproducible data belongs in git. Keep external and large data in cloud storage and record every dataset's provenance and location in a `data/` README or `.md` sidecar so it can be re-downloaded. See [data/README.md](data/README.md)
- **Source code**: Refactor reusable notebook code into `src/{{ module_name }}/` modules
- **Models**: Commit only lightweight models you developed or fine-tuned (about 100 MB, case by case), grouped in purpose-named folders (`embedders/`, `classifiers/`, ...) each with a brief `.md` sidecar. Never commit standard third-party models (e.g. Hugging Face) - move them through model sync (S3). See [models/README.md](models/README.md)
- **Logs**: Write runtime and background-job logs to `logs/` (gitignored); keep a short `logs/README.md` describing each log
- **Temporary files**: Use `tmp/` for scratch and temporary artefacts (gitignored); nothing here is tracked or permanent

## Project Organization

```
├── Makefile           <- Makefile with convenience commands
├── README.md          <- The top-level README for developers
{%- if scaffold_ai == 'Yes' %}
├── ai                 <- Agentic framework and harness resources
{%- endif %}
├── data
│   ├── external       <- Data from third party sources
│   ├── interim        <- Intermediate data that has been transformed
│   ├── processed      <- The final, canonical data sets for modeling
│   └── raw            <- The original, immutable data dump
│
{%- if docs != 'none' %}
├── docs               <- Documentation ({{ docs }})
{%- endif %}
{%- if docker_support == 'Yes' %}
├── docker             <- Docker configuration
{%- endif %}
├── logs               <- Runtime and background-job logs (gitignored)
├── models             <- Trained and serialized models
├── notebooks          <- Jupyter notebooks
├── tmp                <- Scratch space for temporary artefacts (gitignored)
├── pyproject.toml     <- Project configuration and dependencies
├── references         <- Data dictionaries, manuals, explanatory materials
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
