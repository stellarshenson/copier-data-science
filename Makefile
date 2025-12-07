.PHONY: create_environment requirements format lint docs docs-serve test clean manual-test increment_version

VENV = .venv
PYTHON = $(VENV)/bin/python
UV = uv

## Create virtual environment
create_environment:
	$(UV) venv $(VENV)
	$(UV) pip install -e ".[dev]" --python $(PYTHON)

## Install Python Dependencies (requires venv)
requirements:
	$(UV) pip install -e ".[dev]" --python $(PYTHON)

## Format code
format:
	$(VENV)/bin/ruff check --fix scripts tests docs/scripts
	$(VENV)/bin/ruff format scripts tests docs/scripts

## Lint code
lint:
	$(VENV)/bin/ruff check scripts tests docs/scripts
	$(VENV)/bin/ruff format --check scripts tests docs/scripts

## Clean artifacts
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .pytest_cache

## Build docs
docs:
	cd docs && $(CURDIR)/$(VENV)/bin/mkdocs build

## Serve docs locally
docs-serve:
	cd docs && $(CURDIR)/$(VENV)/bin/mkdocs serve

## Run tests
test:
	$(VENV)/bin/pytest -vvv --durations=0 tests

## Manual test - generate project
manual-test:
	rm -rf manual_test
	mkdir -p manual_test
	$(VENV)/bin/copier copy --trust --defaults . manual_test/test_project

## Increment patch version in pyproject.toml
increment_version:
	@current=$$(grep -oP 'version = "\K[0-9]+\.[0-9]+\.[0-9]+' pyproject.toml); \
	major=$$(echo $$current | cut -d. -f1); \
	minor=$$(echo $$current | cut -d. -f2); \
	patch=$$(echo $$current | cut -d. -f3); \
	new_patch=$$((patch + 1)); \
	new_version="$$major.$$minor.$$new_patch"; \
	sed -i "s/version = \"$$current\"/version = \"$$new_version\"/" pyproject.toml; \
	echo "Version bumped: $$current -> $$new_version"
