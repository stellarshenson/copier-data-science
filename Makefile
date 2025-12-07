.PHONY: requirements format lint docs docs-serve test clean manual-test increment_version

## Install Python Dependencies
requirements:
	python -m pip install -e ".[dev]"

## Format code
format:
	isort --profile black scripts tests docs/scripts
	black scripts tests docs/scripts

## Lint code
lint:
	flake8 scripts tests docs/scripts
	isort --check --profile black scripts tests docs/scripts
	black --check scripts tests docs/scripts

## Clean artifacts
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .pytest_cache

## Build docs
docs:
	cd docs && mkdocs build

## Serve docs locally
docs-serve:
	cd docs && mkdocs serve

## Run tests
test:
	pytest -vvv --durations=0 tests

## Manual test - generate project
manual-test:
	rm -rf manual_test
	mkdir -p manual_test
	copier copy --trust --defaults . manual_test/test_project

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
