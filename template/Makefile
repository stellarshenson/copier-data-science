.PHONY: clean data lint format requirements upgrade build sync_data_up sync_data_down sync_models_up sync_models_down test docs docs_serve

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = {{ repo_name }}
MODULE_NAME = {{ module_name }}
PYTHON_VERSION = {{ python_version_number }}
PYTHON_INTERPRETER = python
{%- if dataset_storage != 'none' %}
{%- if dataset_storage == 's3' %}

# AWS S3 configuration
S3_BUCKET = {{ s3_bucket }}
AWS_PROFILE = {{ s3_aws_profile }}
{%- elif dataset_storage == 'azure' %}

# Azure Blob Storage configuration
AZURE_CONTAINER = {{ azure_container }}
{%- elif dataset_storage == 'gcs' %}

# Google Cloud Storage configuration
GCS_BUCKET = {{ gcs_bucket }}
{%- endif %}
{%- endif %}

#################################################################################
# STYLES                                                                        #
#################################################################################

MSG_PREFIX = \033[1m\033[36m>>>\033[0m
WARN_PREFIX = \033[33m>>>\033[0m
ERR_PREFIX = \033[31m>>>\033[0m
WARN_STYLE = \033[33m
ERR_STYLE = \033[31m
HIGHLIGHT_STYLE = \033[1m\033[94m
OK_STYLE = \033[92m
NO_STYLE = \033[0m

#################################################################################
# ENVIRONMENT CONFIGURATION                                                     #
#################################################################################

# unified environment name for all managers
{% if dependency_file == 'environment.yml' -%}
ENV_NAME = $(shell sed -n '/^name:/{ s/^name:[ \t]*//; s/[ \t]*\#.*//; s/[ \t]*$$//p; }' environment.yml)
{% else -%}
ENV_NAME = {{ env_name }}
{% endif -%}

{% if environment_manager == 'conda' -%}
# conda environment configuration
ENV_LOCATION = {{ env_location }}
CONDA_FLAGS = --no-capture-output
CONDA_ENV_PATH = $(PROJECT_DIR)/.venv/$(ENV_NAME)

# set conda env selector based on location (local vs global)
ifeq ($(ENV_LOCATION),local)
CONDA_ENV_SELECTOR = -p $(CONDA_ENV_PATH)
else
CONDA_ENV_SELECTOR = --name $(ENV_NAME)
endif

# check if conda is present
ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

# check if environment was installed
ifeq ($(ENV_LOCATION),local)
ifeq (,$(wildcard $(CONDA_ENV_PATH)/conda-meta))
HAS_CONDA_ENV=False
else
HAS_CONDA_ENV=True
endif
else
ifeq (,$(shell conda env list | grep $(ENV_NAME)))
HAS_CONDA_ENV=False
else
HAS_CONDA_ENV=True
endif
endif

{% elif environment_manager == 'virtualenv' -%}
# virtualenv configuration
VENV_PATH = $(PROJECT_DIR)/.venv
{% elif environment_manager == 'uv' -%}
# uv configuration
VENV_PATH = $(PROJECT_DIR)/.venv
{% endif %}
{% if docker_support == 'Yes' -%}
#################################################################################
# DOCKER CONFIGURATION                                                          #
# Override via environment variables: DOCKER_REGISTRY, DOCKER_IMAGE_NAME,       #
# DOCKER_TAG (Python version uses PYTHON_VERSION from project config)           #
#################################################################################

DOCKER_REGISTRY ?= docker.io
DOCKER_IMAGE_NAME ?= {{ repo_name }}
DOCKER_TAG ?= latest

{% endif -%}
#################################################################################
# COMMANDS                                                                      #
#################################################################################

{%- if dependency_file != 'none' %}
## Install Python dependencies
.PHONY: requirements
{%- if environment_manager == 'conda' %}
requirements: test_environment
	@echo "$(MSG_PREFIX) installing requirements for $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE) environment"
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m pip install -U pip setuptools wheel
{%- if dependency_file == 'environment.yml' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install -e .
{%- elif dependency_file == 'requirements.txt' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m pip install -r requirements.txt
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m pip install -r requirements-dev.txt
{%- elif dependency_file == 'pyproject.toml' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install -e ".[dev]"
{%- endif %}
{%- elif environment_manager == 'virtualenv' %}
requirements:
	@echo "$(MSG_PREFIX) installing requirements"
	$(PYTHON_INTERPRETER) -m pip install -U pip
{%- if dependency_file == 'requirements.txt' %}
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
{%- elif dependency_file == 'pyproject.toml' %}
	pip install -e .
{%- endif %}
{%- elif environment_manager == 'uv' %}
requirements:
	@echo "$(MSG_PREFIX) installing requirements with uv"
{%- if dependency_file == 'requirements.txt' %}
	uv pip install --python $(PROJECT_DIR)/.venv -r requirements.txt
{%- elif dependency_file == 'pyproject.toml' %}
	uv sync --python $(PROJECT_DIR)/.venv --extra dev
{%- endif %}
{%- endif %}
{%- endif %}

{%- if dependency_file != 'none' %}
## Upgrade Python dependencies to latest versions
.PHONY: upgrade
{%- if environment_manager == 'conda' %}
upgrade: test_environment
	@echo "$(MSG_PREFIX) upgrading packages in $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE) environment"
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) conda update --all -y
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m pip install -U pip setuptools wheel
{%- if dependency_file == 'environment.yml' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install --upgrade -e .
{%- elif dependency_file == 'requirements.txt' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m pip install --upgrade -r requirements.txt
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m pip install --upgrade -r requirements-dev.txt
{%- elif dependency_file == 'pyproject.toml' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install --upgrade -e ".[dev]"
{%- endif %}
{%- elif environment_manager == 'virtualenv' %}
upgrade:
	@echo "$(MSG_PREFIX) upgrading packages"
	$(PROJECT_DIR)/.venv/bin/pip install -U pip
{%- if dependency_file == 'requirements.txt' %}
	$(PROJECT_DIR)/.venv/bin/pip install --upgrade -r requirements.txt
	$(PROJECT_DIR)/.venv/bin/pip install --upgrade -r requirements-dev.txt
{%- elif dependency_file == 'pyproject.toml' %}
	$(PROJECT_DIR)/.venv/bin/pip install --upgrade -e ".[dev]"
{%- endif %}
{%- elif environment_manager == 'uv' %}
upgrade:
	@echo "$(MSG_PREFIX) upgrading packages with uv"
{%- if dependency_file == 'requirements.txt' %}
	uv pip install --python $(PROJECT_DIR)/.venv --upgrade -r requirements.txt
{%- elif dependency_file == 'pyproject.toml' %}
	uv sync --python $(PROJECT_DIR)/.venv --extra dev --upgrade
{%- endif %}
{%- endif %}
{%- endif %}

## Delete all compiled Python files
clean:
	@echo "$(MSG_PREFIX) removing cache and compiled files"
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name '__pycache__' -exec rm -r {} +
	@find . -type d -name '*.egg-info' -exec rm -r {} +
	@find . -type d -name '.ipynb_checkpoints' -exec rm -r {} +
	@find . -type d -name '.pytest_cache' -exec rm -r {} +
	@echo "$(MSG_PREFIX) removing dist and build directory"
	@rm -rf build dist

{% if env_encryption == 'Yes' -%}
## Restore .env from encrypted .env.enc (or create empty)
.env:
	@if [ -f ".env.enc" ]; then \
		echo "$(MSG_PREFIX) decrypting .env.enc"; \
		openssl enc -d -aes-256-cbc -pbkdf2 -in .env.enc -out .env || { rm -f .env; echo "$(ERR_PREFIX) $(ERR_STYLE)decryption failed$(NO_STYLE)"; exit 1; }; \
	else \
		echo "$(MSG_PREFIX) creating empty .env"; \
		touch .env; \
	fi

## Encrypt .env to .env.enc (AES-256)
.env.enc: .env
	@echo "$(MSG_PREFIX) encrypting .env"
	@openssl enc -aes-256-cbc -pbkdf2 -in .env -out .env.enc
	@echo "$(OK_STYLE)>>> .env.enc file successfully created$(NO_STYLE)"

{% endif -%}
{% if linting_and_formatting == 'ruff' -%}
## Lint using ruff (use `make format` to do formatting)
lint:
	@echo "$(MSG_PREFIX) linting the sourcecode"
	ruff format --check
	ruff check

## Format source code with ruff
format:
	@echo "$(MSG_PREFIX) formatting the sourcecode"
	ruff check --fix
	ruff format
{%- elif linting_and_formatting == 'flake8+black+isort' -%}
## Lint using flake8, black, and isort (use `make format` to do formatting)
lint:
	@echo "$(MSG_PREFIX) linting the sourcecode"
	flake8 {{ module_name }}
	isort --check --diff {{ module_name }}
	black --check {{ module_name }}

## Format source code with black and isort
format:
	@echo "$(MSG_PREFIX) formatting the sourcecode"
	isort {{ module_name }}
	black {{ module_name }}
{%- endif %}

{%- if testing_framework != 'none' %}
## Run tests
test:
	@echo "$(MSG_PREFIX) checking for tests"
{%- if environment_manager == 'conda' %}
{%- if testing_framework == 'pytest' %}
	@conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pytest --collect-only ./tests > /dev/null 2>&1; RESULT="$$?"; \
	if [ "$$RESULT" != "5" ]; then \
		echo "$(MSG_PREFIX) executing python tests"; \
		conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pytest --cov -v ./tests; \
	else \
		echo "$(WARN_PREFIX) $(WARN_STYLE)WARNING: no tests present$(NO_STYLE)"; \
	fi
{%- elif testing_framework == 'unittest' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m unittest discover -s tests
{%- endif %}
{%- else %}
{%- if testing_framework == 'pytest' %}
	@$(PROJECT_DIR)/.venv/bin/pytest --collect-only ./tests > /dev/null 2>&1; RESULT="$$?"; \
	if [ "$$RESULT" != "5" ]; then \
		echo "$(MSG_PREFIX) executing python tests"; \
		$(PROJECT_DIR)/.venv/bin/pytest --cov -v ./tests; \
	else \
		echo "$(WARN_PREFIX) $(WARN_STYLE)WARNING: no tests present$(NO_STYLE)"; \
	fi
{%- elif testing_framework == 'unittest' %}
	$(PROJECT_DIR)/.venv/bin/python -m unittest discover -s tests
{%- endif %}
{%- endif %}
{%- endif %}

{%- if docs == 'mkdocs' %}
## Build documentation
docs:
	@echo "$(MSG_PREFIX) building documentation"
{%- if environment_manager == 'conda' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) mkdocs build -f docs/mkdocs.yml
{%- else %}
	$(PROJECT_DIR)/.venv/bin/mkdocs build -f docs/mkdocs.yml
{%- endif %}

## Serve documentation locally
docs_serve:
	@echo "$(MSG_PREFIX) serving documentation at http://127.0.0.1:8000"
{%- if environment_manager == 'conda' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) mkdocs serve -f docs/mkdocs.yml
{%- else %}
	$(PROJECT_DIR)/.venv/bin/mkdocs serve -f docs/mkdocs.yml
{%- endif %}
{%- endif %}

{%- if dataset_storage != 'none' %}
## Download data from storage system
sync_data_down:
	@echo "$(MSG_PREFIX) downloading data from storage"
{%- if dataset_storage == 's3' %}
{%- if s3_aws_profile != 'default' %}
	aws s3 sync s3://$(S3_BUCKET)/data/ data/ --profile $(AWS_PROFILE)
{%- else %}
	aws s3 sync s3://$(S3_BUCKET)/data/ data/
{%- endif %}
{%- elif dataset_storage == 'azure' %}
	az storage blob download-batch -s $(AZURE_CONTAINER)/data/ -d data/
{%- elif dataset_storage == 'gcs' %}
	gsutil -m rsync -r gs://$(GCS_BUCKET)/data/ data/
{%- endif %}

## Upload data to storage system
sync_data_up:
	@echo "$(MSG_PREFIX) uploading data to storage"
{%- if dataset_storage == 's3' %}
{%- if s3_aws_profile != 'default' %}
	aws s3 sync data/ s3://$(S3_BUCKET)/data/ --profile $(AWS_PROFILE)
{%- else %}
	aws s3 sync data/ s3://$(S3_BUCKET)/data/
{%- endif %}
{%- elif dataset_storage == 'azure' %}
	az storage blob upload-batch -d $(AZURE_CONTAINER)/data/ -s data/
{%- elif dataset_storage == 'gcs' %}
	gsutil -m rsync -r data/ gs://$(GCS_BUCKET)/data/
{%- endif %}

## Download models from storage system
sync_models_down:
	@echo "$(MSG_PREFIX) downloading models from storage"
{%- if dataset_storage == 's3' %}
{%- if s3_aws_profile != 'default' %}
	aws s3 sync s3://$(S3_BUCKET)/models/ models/ --profile $(AWS_PROFILE)
{%- else %}
	aws s3 sync s3://$(S3_BUCKET)/models/ models/
{%- endif %}
{%- elif dataset_storage == 'azure' %}
	az storage blob download-batch -s $(AZURE_CONTAINER)/models/ -d models/
{%- elif dataset_storage == 'gcs' %}
	gsutil -m rsync -r gs://$(GCS_BUCKET)/models/ models/
{%- endif %}

## Upload models to storage system
sync_models_up:
	@echo "$(MSG_PREFIX) uploading models to storage"
{%- if dataset_storage == 's3' %}
{%- if s3_aws_profile != 'default' %}
	aws s3 sync models/ s3://$(S3_BUCKET)/models/ --profile $(AWS_PROFILE)
{%- else %}
	aws s3 sync models/ s3://$(S3_BUCKET)/models/
{%- endif %}
{%- elif dataset_storage == 'azure' %}
	az storage blob upload-batch -d $(AZURE_CONTAINER)/models/ -s models/
{%- elif dataset_storage == 'gcs' %}
	gsutil -m rsync -r models/ gs://$(GCS_BUCKET)/models/
{%- endif %}
{%- endif %}

{%- if environment_manager == 'conda' %}
#################################################################################
# CONDA ENVIRONMENT MANAGEMENT                                                  #
#################################################################################

## Check conda is available
check_conda:
ifeq (False,$(HAS_CONDA))
	@echo "$(ERR_PREFIX) $(ERR_STYLE)ERROR: conda not installed$(NO_STYLE)"
	@echo "$(ERR_PREFIX) $(ERR_STYLE)install anaconda or miniforge from https://github.com/conda-forge/miniforge$(NO_STYLE)"
	@exit 1
endif

## Set up conda environment
create_environment: check_conda
ifeq (True,$(HAS_CONDA))
ifeq ($(ENV_LOCATION),local)
	@echo "$(MSG_PREFIX) detected conda. Checking if local environment exists at .venv/$(ENV_NAME)"
	@if [ -d "$(CONDA_ENV_PATH)/conda-meta" ]; then \
		echo "$(MSG_PREFIX) local conda environment already exists at .venv/$(ENV_NAME). Skipping creation."; \
	else \
		echo "$(MSG_PREFIX) creating new local conda environment at $(HIGHLIGHT_STYLE).venv/$(ENV_NAME)$(NO_STYLE)"; \
{%- if dependency_file == 'environment.yml' %}
		conda env create -p $(CONDA_ENV_PATH) -f environment.yml; \
{%- else %}
		conda create -p $(CONDA_ENV_PATH) python={{ python_version_number }} pip -y -q; \
{%- endif %}
		echo "$(MSG_PREFIX) new conda env created successfully. Activate with: $(HIGHLIGHT_STYLE)conda activate $(CONDA_ENV_PATH)$(NO_STYLE)"; \
		echo "$(MSG_PREFIX) installing dependencies"; \
{%- if dependency_file == 'requirements.txt' %}
		conda run -p $(CONDA_ENV_PATH) $(CONDA_FLAGS) pip install -q -r requirements.txt -r requirements-dev.txt; \
{%- elif dependency_file == 'pyproject.toml' %}
		conda run -p $(CONDA_ENV_PATH) $(CONDA_FLAGS) pip install -q -e ".[dev]"; \
{%- endif %}
		conda run -p $(CONDA_ENV_PATH) $(CONDA_FLAGS) nbdime config-git --enable --global; \
		echo "$(MSG_PREFIX) environment was configured to integrate git with jupyter notebooks"; \
{%- if jupyter_kernel_support == 'Yes' %}
		if python -c "import nb_conda_kernels" 2>/dev/null; then \
			echo "$(MSG_PREFIX) nb_conda_kernels detected - kernel will be auto-discovered"; \
		else \
			echo "$(MSG_PREFIX) registering Jupyter kernel with ipykernel"; \
			conda run -p $(CONDA_ENV_PATH) $(CONDA_FLAGS) python -m ipykernel install --user --name=$(ENV_NAME) --display-name "Python [conda env:$(ENV_NAME)]"; \
			echo "$(OK_STYLE)>>> Kernel registered as $(ENV_NAME)$(NO_STYLE)"; \
		fi; \
{%- endif %}
	fi
else
	@echo "$(MSG_PREFIX) detected conda. Checking if environment $(ENV_NAME) exists."
	@if conda info --envs | grep -q "^$(ENV_NAME)"; then \
		echo "$(MSG_PREFIX) conda environment $(ENV_NAME) already exists. Skipping creation."; \
	else \
		echo "$(MSG_PREFIX) creating new conda environment $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"; \
{%- if dependency_file == 'environment.yml' %}
		conda env create -f environment.yml; \
{%- else %}
		conda create -n $(ENV_NAME) python={{ python_version_number }} pip -y -q; \
{%- endif %}
		echo "$(MSG_PREFIX) new conda env created successfully. Activate with: $(HIGHLIGHT_STYLE)conda activate $(ENV_NAME)$(NO_STYLE)"; \
		echo "$(MSG_PREFIX) installing dependencies"; \
{%- if dependency_file == 'requirements.txt' %}
		conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install -q -r requirements.txt -r requirements-dev.txt; \
{%- elif dependency_file == 'pyproject.toml' %}
		conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install -q -e ".[dev]"; \
{%- endif %}
		conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) nbdime config-git --enable --global; \
		echo "$(MSG_PREFIX) environment $(ENV_NAME) was configured to integrate git with jupyter notebooks"; \
{%- if jupyter_kernel_support == 'Yes' %}
		if python -c "import nb_conda_kernels" 2>/dev/null; then \
			echo "$(MSG_PREFIX) nb_conda_kernels detected - kernel will be auto-discovered"; \
		else \
			echo "$(MSG_PREFIX) registering Jupyter kernel with ipykernel"; \
			conda run --name $(ENV_NAME) $(CONDA_FLAGS) python -m ipykernel install --user --name=$(ENV_NAME) --display-name "Python [conda env:$(ENV_NAME)]"; \
			echo "$(OK_STYLE)>>> Kernel registered as $(ENV_NAME)$(NO_STYLE)"; \
		fi; \
{%- endif %}
	fi
endif
endif

## Remove previously created environment
remove_environment: check_conda
ifeq (True,$(HAS_CONDA))
ifeq ($(ENV_LOCATION),local)
	@echo "$(MSG_PREFIX) detected conda, removing local environment at $(HIGHLIGHT_STYLE).venv/$(ENV_NAME)$(NO_STYLE)"
{%- if jupyter_kernel_support == 'Yes' %}
	@echo "$(MSG_PREFIX) unregistering Jupyter kernel $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"
	@jupyter kernelspec uninstall -y $(ENV_NAME) >/dev/null 2>&1 || true
	@-rm -rf ~/.local/share/jupyter/kernels/$(ENV_NAME) 2>/dev/null || true
{%- endif %}
	conda env remove -y -p $(CONDA_ENV_PATH)
	@rm -rf $(PROJECT_DIR)/.venv
	@echo "$(OK_STYLE)>>> Environment removed$(NO_STYLE)"
else
	@echo "$(MSG_PREFIX) detected conda, removing $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE) conda environment."
{%- if jupyter_kernel_support == 'Yes' %}
	@echo "$(MSG_PREFIX) unregistering Jupyter kernel $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"
	@jupyter kernelspec uninstall -y $(ENV_NAME) >/dev/null 2>&1 || true
	@-rm -rf ~/.local/share/jupyter/kernels/$(ENV_NAME) 2>/dev/null || true
{%- endif %}
	conda env remove -y -n $(ENV_NAME)
	@echo "$(OK_STYLE)>>> Environment removed$(NO_STYLE)"
endif
endif

## Test python environment is setup correctly
test_environment: check_conda
ifeq ($(ENV_LOCATION),local)
	@echo "$(MSG_PREFIX) testing local environment at $(HIGHLIGHT_STYLE).venv/$(ENV_NAME)$(NO_STYLE) if ready"
	@if [ ! -d "$(CONDA_ENV_PATH)/conda-meta" ]; then \
		echo "$(ERR_PREFIX) $(ERR_STYLE)ERROR: local environment not found at .venv/$(ENV_NAME)$(NO_STYLE)"; \
		exit 1; \
	fi
	@echo "$(MSG_PREFIX) checking Python version"
	@conda run -p $(CONDA_ENV_PATH) $(CONDA_FLAGS) python --version
	@echo "$(OK_STYLE)>>> Local environment .venv/$(ENV_NAME) is properly configured$(NO_STYLE)"
else
	@echo "$(MSG_PREFIX) testing environment $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE) if ready"
	@if ! conda env list | grep -q "^$(ENV_NAME) "; then \
		echo "$(ERR_PREFIX) $(ERR_STYLE)ERROR: environment $(ENV_NAME) not found$(NO_STYLE)"; \
		exit 1; \
	fi
	@echo "$(MSG_PREFIX) checking Python version"
	@conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python --version
	@echo "$(OK_STYLE)>>> Environment $(ENV_NAME) is properly configured$(NO_STYLE)"
endif

{%- elif environment_manager == 'virtualenv' %}
#################################################################################
# VIRTUALENV ENVIRONMENT MANAGEMENT                                             #
#################################################################################

## Set up Python interpreter environment
create_environment:
	@if [ -d "$(PROJECT_DIR)/.venv" ]; then \
		echo "$(MSG_PREFIX) virtual environment already exists at $(HIGHLIGHT_STYLE).venv$(NO_STYLE). Skipping creation."; \
	else \
		echo "$(MSG_PREFIX) creating virtualenv environment"; \
		echo "$(MSG_PREFIX) using standard venv"; \
		$(PYTHON_INTERPRETER) -m venv .venv; \
		echo "$(MSG_PREFIX) new virtual environment created at .venv/"; \
		echo "$(MSG_PREFIX) Activate with:"; \
		echo "$(MSG_PREFIX) Windows: $(HIGHLIGHT_STYLE).\\.venv\\Scripts\\activate$(NO_STYLE)"; \
		echo "$(MSG_PREFIX) Unix/macOS: $(HIGHLIGHT_STYLE)source .venv/bin/activate$(NO_STYLE)"; \
		echo "$(MSG_PREFIX) installing dependencies"; \
{%- if dependency_file == 'pyproject.toml' %}
		$(PROJECT_DIR)/.venv/bin/pip install -q -e ".[dev]"; \
{%- else %}
		$(PROJECT_DIR)/.venv/bin/pip install -q -r requirements.txt -r requirements-dev.txt; \
{%- endif %}
{%- if jupyter_kernel_support == 'Yes' %}
		if command -v nb_venv_kernels >/dev/null 2>&1; then \
			echo "$(MSG_PREFIX) registering Jupyter kernel for $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"; \
			nb_venv_kernels register --name $(ENV_NAME) $(PROJECT_DIR)/.venv >/dev/null 2>&1; \
			echo "$(OK_STYLE)>>> Kernel registered successfully$(NO_STYLE)"; \
		else \
			echo "$(MSG_PREFIX) registering Jupyter kernel with ipykernel"; \
			$(PROJECT_DIR)/.venv/bin/python -m ipykernel install --user --name=$(ENV_NAME) --display-name "Python [venv env:$(ENV_NAME)]"; \
			echo "$(OK_STYLE)>>> Kernel registered as $(ENV_NAME)$(NO_STYLE)"; \
		fi; \
{%- endif %}
	fi

## Remove previously created environment
remove_environment:
	@echo "$(MSG_PREFIX) removing virtual environment at $(HIGHLIGHT_STYLE).venv$(NO_STYLE)"
{%- if jupyter_kernel_support == 'Yes' %}
	@echo "$(MSG_PREFIX) unregistering Jupyter kernel $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"
	@if command -v nb_venv_kernels >/dev/null 2>&1; then \
		nb_venv_kernels unregister $(PROJECT_DIR)/.venv >/dev/null 2>&1 || true; \
	else \
		jupyter kernelspec uninstall -y $(ENV_NAME) >/dev/null 2>&1 || true; \
	fi
	@-rm -rf ~/.local/share/jupyter/kernels/$(ENV_NAME) 2>/dev/null || true
{%- endif %}
	@rm -rf $(PROJECT_DIR)/.venv
	@echo "$(OK_STYLE)>>> Environment removed$(NO_STYLE)"

## Install src modules (editable)
install: create_environment requirements clean{% if env_encryption == 'Yes' %} .env{% endif %}

	@echo "$(MSG_PREFIX) installing $(MODULE_NAME) in editable mode"
	$(PROJECT_DIR)/.venv/bin/pip install -e .
	@echo "$(OK_STYLE)>>> $(MODULE_NAME) installed$(NO_STYLE)"

## Build package
build: clean install test increment_build_number
	@echo "$(MSG_PREFIX) building $(MODULE_NAME)"
	$(PROJECT_DIR)/.venv/bin/python -m build --wheel

## Increment build number
increment_build_number:
	@echo "$(MSG_PREFIX) incrementing build number"
	@$(PROJECT_DIR)/.venv/bin/python -c "import toml; data=toml.load('pyproject.toml'); ver=data['project']['version'].split('.'); ver[-1]=str(int(ver[-1])+1); data['project']['version']='.'.join(ver); f=open('pyproject.toml','w'); toml.dump(data,f); f.close(); print('New version:',data['project']['version'])"

{%- elif environment_manager == 'uv' %}
#################################################################################
# UV ENVIRONMENT MANAGEMENT                                                     #
#################################################################################

## Set up Python interpreter environment
create_environment:
	@if [ -d "$(PROJECT_DIR)/.venv" ]; then \
		echo "$(MSG_PREFIX) virtual environment already exists at $(HIGHLIGHT_STYLE).venv$(NO_STYLE). Skipping creation."; \
	else \
		echo "$(MSG_PREFIX) creating uv virtual environment"; \
		uv venv -q --python $(PYTHON_VERSION); \
		echo "$(MSG_PREFIX) new uv virtual environment created. Activate with:"; \
		echo "$(MSG_PREFIX) Windows: $(HIGHLIGHT_STYLE).\\\.venv\\\Scripts\\\activate$(NO_STYLE)"; \
		echo "$(MSG_PREFIX) Unix/macOS: $(HIGHLIGHT_STYLE)source ./.venv/bin/activate$(NO_STYLE)"; \
		echo "$(MSG_PREFIX) installing dependencies"; \
{%- if dependency_file == 'pyproject.toml' %}
		uv pip install -q --python $(PROJECT_DIR)/.venv -e ".[dev]"; \
{%- else %}
		uv pip install -q --python $(PROJECT_DIR)/.venv -r requirements.txt -r requirements-dev.txt; \
{%- endif %}
{%- if jupyter_kernel_support == 'Yes' %}
		if command -v nb_venv_kernels >/dev/null 2>&1; then \
			echo "$(MSG_PREFIX) registering Jupyter kernel for $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"; \
			nb_venv_kernels register --name $(ENV_NAME) $(PROJECT_DIR)/.venv >/dev/null 2>&1; \
			echo "$(OK_STYLE)>>> Kernel registered successfully$(NO_STYLE)"; \
		else \
			echo "$(MSG_PREFIX) registering Jupyter kernel with ipykernel"; \
			$(PROJECT_DIR)/.venv/bin/python -m ipykernel install --user --name=$(ENV_NAME) --display-name "Python [uv env:$(ENV_NAME)]"; \
			echo "$(OK_STYLE)>>> Kernel registered as $(ENV_NAME)$(NO_STYLE)"; \
		fi; \
{%- endif %}
	fi

## Remove previously created environment
remove_environment:
	@echo "$(MSG_PREFIX) removing uv virtual environment at $(HIGHLIGHT_STYLE).venv$(NO_STYLE)"
{%- if jupyter_kernel_support == 'Yes' %}
	@echo "$(MSG_PREFIX) unregistering Jupyter kernel $(HIGHLIGHT_STYLE)$(ENV_NAME)$(NO_STYLE)"
	@if command -v nb_venv_kernels >/dev/null 2>&1; then \
		nb_venv_kernels unregister $(PROJECT_DIR)/.venv >/dev/null 2>&1 || true; \
	else \
		jupyter kernelspec uninstall -y $(ENV_NAME) >/dev/null 2>&1 || true; \
	fi
	@-rm -rf ~/.local/share/jupyter/kernels/$(ENV_NAME) 2>/dev/null || true
{%- endif %}
	@rm -rf $(PROJECT_DIR)/.venv
	@echo "$(OK_STYLE)>>> Environment removed$(NO_STYLE)"

## Install src modules (editable)
install: create_environment requirements clean{% if env_encryption == 'Yes' %} .env{% endif %}

	@echo "$(MSG_PREFIX) installing $(MODULE_NAME) in editable mode"
	@uv pip install -q --python $(PROJECT_DIR)/.venv -e .
	@echo "$(OK_STYLE)>>> $(MODULE_NAME) installed$(NO_STYLE)"

## Build package
build: clean install test increment_build_number
	@echo "$(MSG_PREFIX) building $(MODULE_NAME)"
	$(PROJECT_DIR)/.venv/bin/python -m build --wheel

## Increment build number
increment_build_number:
	@echo "$(MSG_PREFIX) incrementing build number"
	@$(PROJECT_DIR)/.venv/bin/python -c "import toml; data=toml.load('pyproject.toml'); ver=data['project']['version'].split('.'); ver[-1]=str(int(ver[-1])+1); data['project']['version']='.'.join(ver); f=open('pyproject.toml','w'); toml.dump(data,f); f.close(); print('New version:',data['project']['version'])"

{%- endif %}

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

{%- if include_code_scaffold == 'Yes' %}
## Make dataset
data: requirements
	@echo "$(MSG_PREFIX) generating dataset"
{%- if environment_manager == 'conda' %}
	conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) $(PYTHON_INTERPRETER) {{ module_name }}/dataset.py
{%- else %}
	$(PYTHON_INTERPRETER) {{ module_name }}/dataset.py
{%- endif %}
{%- endif %}

{%- if environment_manager == 'conda' %}
## Install src modules without dependencies (editable)
install: check_conda clean create_environment{% if env_encryption == 'Yes' %} .env{% endif %}

	@echo "$(MSG_PREFIX) installing $(MODULE_NAME) in the $(ENV_NAME) environment $(OK_STYLE)EDITABLE$(NO_STYLE)"
	@conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) pip install --editable .
	@echo "$(MSG_PREFIX) you can now import $(HIGHLIGHT_STYLE)$(MODULE_NAME)$(NO_STYLE) module in your notebooks and scripts\n"

## Build package and install
build: check_conda clean install test increment_build_number
	@echo "$(MSG_PREFIX) building $(MODULE_NAME)"
	@conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -m build --wheel

## Increment build number
increment_build_number: check_conda
	@echo "$(MSG_PREFIX) incrementing build number"
	@conda run $(CONDA_ENV_SELECTOR) $(CONDA_FLAGS) python -c "import toml; data=toml.load('pyproject.toml'); ver=data['project']['version'].split('.'); ver[-1]=str(int(ver[-1])+1); data['project']['version']='.'.join(ver); f=open('pyproject.toml','w'); toml.dump(data,f); f.close(); print('New version:',data['project']['version'])"
{%- endif %}

{% if docker_support == 'Yes' -%}
#################################################################################
# DOCKER                                                                        #
#################################################################################

## Build Docker image
docker_build: build
	@echo "$(MSG_PREFIX) building Docker image $(HIGHLIGHT_STYLE)$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)$(NO_STYLE) (Python $(PYTHON_VERSION))"
	docker build --build-arg PYTHON_VERSION=$(PYTHON_VERSION) -t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) -f docker/Dockerfile .
	@echo "$(OK_STYLE)>>> Docker image built successfully$(NO_STYLE)"

## Run Docker container
docker_run: docker_build
	@echo "$(MSG_PREFIX) running Docker container $(HIGHLIGHT_STYLE)$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)$(NO_STYLE)"
	docker run --rm $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
	@echo "$(OK_STYLE)>>> Docker container finished$(NO_STYLE)"

## Push Docker image to registry
docker_push: docker_build
	@echo "$(MSG_PREFIX) pushing Docker image to $(HIGHLIGHT_STYLE)$(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)$(NO_STYLE)"
	docker tag $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
	@echo "$(OK_STYLE)>>> Docker image pushed successfully$(NO_STYLE)"

{% endif -%}
#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = sys.stdin.read(); \
matches = re.findall(r'\n## ([^\n]+)\n(?!\.PHONY)([a-zA-Z_.][a-zA-Z0-9_.-]*):', lines); \
matches = sorted(matches, key=lambda x: x[1].lower()); \
print('\nAvailable rules:\n'); \
print('\n'.join(['\033[36m{:25}\033[0m{}'.format(*reversed(match)) for match in matches])); \
print()
endef
export PRINT_HELP_PYSCRIPT

## Print the list of available commands
help:
	@$(PYTHON_INTERPRETER) -c "$${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)

# EOF
