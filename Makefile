PYTHON = python3
PYENV_VERSION = 3.9.13
VENV = .venv


.PHONY: all
DEFAULT_GOAL: setup

setup: get_pyenv venv

venv: $(VENV)/touchfile # wrapper for the one below

get_pyenv:
	@echo "installing pyenv via homebrew and python$(PYTHON_VERSION)"
	brew install pyenv
	pyenv install -v $(PYTHON_VERSION) || true # to avoid cancelling the recipe if existing

# only when requirements change: https://stackoverflow.com/questions/24736146/how-to-use-virtualenv-in-makefile
.ONESHELL:
$(VENV)/touchfile: requirements.txt requirements-dev.txt
	@pyenv local $(PYENV_VERSION) || { echo "!!! no python $(PYENV_VERSION) found run 'make get_pyenv' to install it"; exit 1; }
	@echo "Creating virtual environment and installing dependencies in $(VENV) using python $(PYENV_VERSION)"
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip \
	&& pip install -r requirements.txt && pip install -r requirements-dev.txt
	@touch $(VENV)/touchfile
	rm -rf .python-version


update: # to force the upper
	. $(VENV)/bin/activate && pip install --upgrade pip \
	&& pip install -r requirements.txt && pip install -r requirements_dev.txt

format:
	nbqa isort .
	nbqa black . --exclude '/(outputs|\.ipynb_checkpoints)/'
	nbqa autoflake . -i --remove-all-unused-imports --exclude '/(outputs|\.ipynb_checkpoints)/'

cleanup:
	@echo "Cleaning up the envs / temps."
	@rm -rf $(VENV)/
	# TODO more to be deleted?
