#!/bin/bash
set -ex

# Clean any parent .venv from PATH to avoid python resolution conflicts
# This happens when tests run from an activated virtualenv
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '\.venv' | tr '\n' ':' | sed 's/:$//')

PROJECT_NAME=$(basename $1)
CCDS_ROOT=$(dirname $0)
MODULE_NAME=$2

# configure exit / teardown behavior
function finish {
    # Deactivate venv if we're in one
    if [[ $(which python) == *".venv"* ]] || [[ $(which python) == *"$PROJECT_NAME"* ]]; then
        deactivate || true
    fi

    # Clean up virtualenvwrapper env if it exists
    if [ ! -z `which rmvirtualenv` ]; then
        rmvirtualenv $PROJECT_NAME 2>/dev/null || true
    fi
    # Clean up .venv directory
    if [ -d ".venv" ]; then
        rm -rf .venv
    fi

    # Remove Jupyter kernel if registered
    if [ -d "$HOME/.local/share/jupyter/kernels/$PROJECT_NAME" ]; then
        rm -rf "$HOME/.local/share/jupyter/kernels/$PROJECT_NAME"
    fi
}
trap finish EXIT

# source the steps in the test
source $CCDS_ROOT/test_functions.sh

# navigate to the generated project and run make commands
cd $1

make
make create_environment

# Activate the virtualenv - check both standard venv and virtualenvwrapper locations
if [ -e ".venv/bin/activate" ]; then
    # Standard venv in project directory
    source ".venv/bin/activate"
elif [ -e ".venv/Scripts/activate" ]; then
    # Standard venv on Windows
    source ".venv/Scripts/activate"
elif [ ! -z "$WORKON_HOME" ] && [ -e "$WORKON_HOME/$PROJECT_NAME/bin/activate" ]; then
    # virtualenvwrapper on Unix
    source "$WORKON_HOME/$PROJECT_NAME/bin/activate"
elif [ ! -z "$WORKON_HOME" ] && [ -e "$WORKON_HOME/$PROJECT_NAME/Scripts/activate" ]; then
    # virtualenvwrapper on Windows
    source "$WORKON_HOME/$PROJECT_NAME/Scripts/activate"
else
    echo "ERROR: Could not find virtualenv to activate"
    exit 1
fi

make requirements
make lint
make format

# Test clean target
mkdir -p __pycache__
touch __pycache__/test.pyc
make clean
if [ -d "__pycache__" ]; then
    echo "ERROR: clean did not remove __pycache__"
    exit 1
fi

echo "All targets passed!"
