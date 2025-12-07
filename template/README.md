# {{ project_name }}

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

{{ description }}

## Quick Start

```bash
make install
```

## Makefile Targets

- `make install` - Create environment and install package
- `make test` - Run tests
- `make lint` / `make format` - Check / fix code style
- `make build` - Build distributable wheel
- `make clean` - Remove compiled files and caches
{%- if docs == 'mkdocs' %}
- `make docs` / `make docs_serve` - Build / serve documentation
{%- endif %}
{%- if dataset_storage != 'none' %}
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

- **Notebooks**: Name with number prefix, initials, description - `1.0-jqp-data-exploration.ipynb`
- **Data**: Keep `raw/` immutable, use `interim/` for transforms, `processed/` for final datasets
- **Source code**: Refactor reusable notebook code into `{{ module_name }}/` modules
- **Models**: Store trained models in `models/` with clear naming

## Project Organization

```
├── Makefile           <- Makefile with convenience commands
├── README.md          <- The top-level README for developers
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
├── models             <- Trained and serialized models
├── notebooks          <- Jupyter notebooks
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
