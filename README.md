# Copier Data Science

_A logical, reasonably standardized but flexible project structure for doing and sharing data science work._

[![integration-tests](https://github.com/stellarshenson/copier-data-science/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/stellarshenson/copier-data-science/actions/workflows/integration-tests.yml)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Inspired by CCDS](https://img.shields.io/badge/CCDS-Inspired%20by-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/)
[![Brought To You By KOLOMOLO](https://img.shields.io/badge/Brought%20To%20You%20By-KOLOMOLO-00ffff?style=flat)](https://kolomolo.com)
[![Donate PayPal](https://img.shields.io/badge/Donate-PayPal-blue?style=flat)](https://www.paypal.com/donate/?hosted_button_id=B4KPBJDLLXTSA)

> [!NOTE]
> This project is based on the excellent [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) by [DrivenData](https://drivendata.co/). We use [Copier](https://copier.readthedocs.io/) instead of Cookiecutter to enable template updates for existing projects. See [Philosophy Document](docs/docs/stellars-philosophy.md) for what makes this fork different.

## Key Features

| Feature | Original ccds | This Template |
|---------|--------------|----------------|
| Template engine | Cookiecutter | Copier (with update support) |
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

**Key enhancements:**
- **Copier template** - Template updates with `copier update`, answers stored in `.copier-answers.yml`
- **uv default** - Modern, fast Python package manager
- **Local environments** - `.venv/` directory for project isolation
- **`lib_` prefix** - Clear module naming (`lib_myproject/`)
- **Dev/prod separation** - Development tools separate from production dependencies
- **Zero boilerplate** - Jupyter kernel, linting, testing pre-configured
- **Environment checks** - Skip creation if environment exists
- **Model sync** - `sync_models_up/down` targets for cloud storage
- **.env encryption** - Optional AES-256 encryption for secrets (`make .env.enc`)
- **Build versioning** - Auto-increment build number in pyproject.toml on `make build`
- **Docker support** - Optional Dockerfile and Makefile targets (`docker_build`, `docker_run`, `docker_push`)

This template uses [nb_venv_kernels](https://github.com/stellarshenson/nb_venv_kernels) for automatic Jupyter kernel management - your project environments appear as kernels in JupyterLab without manual registration. For conda environments, [nb_conda_kernels](https://github.com/Anaconda-Platform/nb_conda_kernels) is used instead. Both provide automatic kernel discovery and cleanup when environments are removed.

## Installation

Requires Python 3.9+. We recommend installing Copier with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install copier
```

## Starting a new project

```bash
copier copy --trust gh:stellarshenson/copier-data-science my-project
```

Then follow the prompts, and once created:

```bash
cd my-project
make install   # Creates environment, installs dev tools and module
```

## Updating an existing project

One of Copier's key advantages is the ability to update projects when the template changes:

```bash
cd my-project
copier update --trust
```

This will merge template updates while preserving your customizations. Your original answers are stored in `.copier-answers.yml`.

### The resulting directory structure

The directory structure of your new project will look something like this (depending on the settings that you choose):

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make install` or `make test`
├── README.md          <- The top-level README for developers using this project
├── pyproject.toml     <- Project configuration with package metadata and dev dependencies
├── .copier-answers.yml <- Copier answers for template updates
│
├── data
│   ├── external       <- Data from third party sources
│   ├── interim        <- Intermediate data that has been transformed
│   ├── processed      <- The final, canonical data sets for modeling
│   └── raw            <- The original, immutable data dump
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
├── models             <- Trained and serialized models, model predictions, or model summaries
├── notebooks          <- Jupyter notebooks (naming: `01-initials-description.ipynb`)
├── references         <- Data dictionaries, manuals, and all other explanatory materials
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── environment.yml    <- conda only: development dependencies
├── requirements-dev.txt <- virtualenv only: development dependencies
│
└── lib_<project_name>/  <- Source code module (installable with pip install -e .)
    ├── __init__.py
    ├── config.py        <- Store useful variables and configuration
    ├── dataset.py       <- Scripts to download or generate data
    ├── features.py      <- Code to create features for modeling
    ├── plots.py         <- Code to create visualizations
    └── modeling/
        ├── __init__.py
        ├── predict.py   <- Code to run model inference with trained models
        └── train.py     <- Code to train models
```

## Upstream

This project builds on the excellent work of [DrivenData's Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science). See the [upstream documentation](https://cookiecutter-data-science.drivendata.org/) for the original project and its philosophy.

## Contributing

Contributions welcome! Fork, make changes, and submit a PR.

### Running the tests

```bash
pip install -r dev-requirements.txt
pytest tests -v
```

Fast mode for quick iteration:

```bash
pytest tests -F   # Single config
pytest tests -FF  # Skip Makefile validation
pytest tests -FFF # Both
```
