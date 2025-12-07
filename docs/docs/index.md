# Copier Data Science

_A logical, flexible, and reasonably standardized project structure for doing and sharing data science work._

[![tests](https://github.com/stellarshenson/copier-data-science/actions/workflows/tests.yml/badge.svg)](https://github.com/stellarshenson/copier-data-science/actions/workflows/tests.yml)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Inspired by CCDS](https://img.shields.io/badge/CCDS-Inspired%20by-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/)

This template uses [Copier](https://copier.readthedocs.io/) for project generation with template update support. It is a fork of DrivenData's [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) with enhanced features for data science workflows.

## Quickstart

Requires Python 3.9+. We recommend installing Copier with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install copier
```

## Starting a new project

Starting a new project is as easy as running this command at the command line:

```bash
copier copy --trust gh:stellarshenson/copier-data-science my-project
```

The `--trust` flag is required because the template uses Jinja extensions and post-generation tasks.

Now that you've got your project, you're ready to go! You should do the following:

 - **Check out the directory structure** below so you know what's in the project and how to use it.
 - **Read the [opinions](opinions.md)** that are baked into the project so you understand best practices and the philosophy behind the project structure.
 - **Read the [using the template](using-the-template.md) guide** to understand how to get started on a project that uses the template.

 Enjoy!


## Directory structure

The directory structure of your new project will look something like this (depending on the settings that you choose):

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make install` or `make test`
├── README.md          <- The top-level README for developers using this project.
├── .copier-answers.yml <- Copier answers for template updates
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for
│                         lib_<project_name> and configuration for tools like ruff
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment
│
├── setup.cfg          <- Configuration file for flake8 (if using flake8+black+isort)
│
└── lib_<project_name>   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes lib_<project_name> a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling
    │   ├── __init__.py
    │   ├── predict.py          <- Code to run model inference with trained models
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

## Updating Projects

One of Copier's key advantages is updating existing projects when the template changes:

```bash
cd my-existing-project
copier update --trust
```

This will merge template updates while preserving your customizations. Your original answers are stored in `.copier-answers.yml`.
