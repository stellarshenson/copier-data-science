#!/bin/bash
set -ex

# Clean any parent .venv from PATH to avoid python resolution conflicts
# This happens when tests run from an activated virtualenv
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '\.venv' | tr '\n' ':' | sed 's/:$//')

# enable conda commands inside the script
eval "$(conda shell.bash hook)"

PROJECT_NAME=$(basename $1)
CCDS_ROOT=$(dirname $0)
MODULE_NAME=$2
ENV_LOCATION=${3:-local}
ENV_NAME=${4:-$PROJECT_NAME}

# configure exit / teardown behavior
function finish {
    if [[ $(which python) == *"$ENV_NAME"* ]] || [[ $(which python) == *".venv"* ]]; then
        conda deactivate
    fi

    if [[ "$ENV_LOCATION" == "local" ]]; then
        # Remove local environment
        if [ -d ".venv/$ENV_NAME" ]; then
            conda env remove -p ".venv/$ENV_NAME" -y || true
        fi
    else
        # Remove global environment
        conda env remove -n $ENV_NAME -y || true
    fi

    # Remove Jupyter kernel if registered
    if [ -d "$HOME/.local/share/jupyter/kernels/$ENV_NAME" ]; then
        rm -rf "$HOME/.local/share/jupyter/kernels/$ENV_NAME"
    fi
}
trap finish EXIT

# source the steps in the test
source $CCDS_ROOT/test_functions.sh

# navigate to the generated project and run make commands
cd $1

# Fix for conda issue https://github.com/conda/conda/issues/7267 on MacOS
if [ -e /usr/local/miniconda ]
then
    sudo chown -R $USER /usr/local/miniconda
fi

make
make create_environment

# Activate based on environment location
if [[ "$ENV_LOCATION" == "local" ]]; then
    conda activate ".venv/$ENV_NAME"
else
    conda activate $ENV_NAME
fi

make requirements
make lint
make format

# Test install target (conda only)
make install

# Test clean target
mkdir -p __pycache__
touch __pycache__/test.pyc
make clean
if [ -d "__pycache__" ]; then
    echo "ERROR: clean did not remove __pycache__"
    exit 1
fi

# Test remove_environment (must deactivate first)
conda deactivate
make remove_environment
if [[ "$ENV_LOCATION" == "local" ]]; then
    if [ -d ".venv/$ENV_NAME/conda-meta" ]; then
        echo "ERROR: remove_environment did not remove local env"
        exit 1
    fi
else
    if conda env list | grep -q "^$ENV_NAME "; then
        echo "ERROR: remove_environment did not remove global env"
        exit 1
    fi
fi

echo "All targets passed!"
