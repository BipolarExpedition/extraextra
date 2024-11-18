# Variables
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
SH := /bin/sh
PIP := $(VENV_DIR)/bin/pip
UPDATE_SCRIPT := scripts/update-variables.sh
SRC := src
REQ_FILE := requirements.txt
DEV_REQ_FILE := requirements-dev.txt
DOC_SRC := docs/source
DOC_BUILD := docs/build
SPHINXBUILD := $(VENV_DIR)/bin/sphinx-build
COV_HTML := coverage_html_report
PROJECT_VERSION := 0.0.1
AUTHOR_NAME := "BipolarExpedition(Doc1979)"
AUTHOR_EMAIL := "lastdoc39@gmail.com"

# This makefile is a work in progress. It currently does not
#    support any of the functions you would expect. The only
#    functions you can use are update-metadata

# Update metadata in files
.PHONY: update-metadata
update-metadata:
	$(SH) $(UPDATE_SCRIPT)
	@echo "Metadata updated in source files."

# # Setup environment
# .PHONY: setup
# setup:
# 	rm -rf $(VENV_DIR)
# 	python3 -m venv $(VENV_DIR)
# 	$(PIP) install -r $(REQ_FILE)

# .PHONY: setup-dev
# setup-dev:
# 	rm -rf $(VENV_DIR)
# 	python3 -m venv $(VENV_DIR)
# 	$(PIP) install -r $(DEV_REQ_FILE)

# Default target: help
.PHONY: help
help: 
	@echo "Available targets:"
	@echo "  help                - Show this help message"
# 	@echo "  setup               - Set up virtual environment and install dependencies"
# 	@echo "  clean               - Clean up the project directory"
# 	@echo "  build               - Build the project with hatch"
# 	@echo "  pyinstaller-package - Package the project with PyInstaller for Windows"
# 	@echo "  test                - Run tests with pytest"
# 	@echo "  coverage            - Run tests and check coverage"
# 	@echo "  format              - Format code with ruff"
# 	@echo "  run                 - Run the project (in venv)"
# 	@echo "  debug               - Run the project with debugging enabled"
# 	@echo "  changelog           - Generate a changelog since the last commit"
# 	@echo "  deps                - Check for outdated dependencies"
# 	@echo "  docs-html           - Generate HTML documentation"
# 	@echo "  docs-pdf            - Generate PDF documentation"
# 	@echo "  docs                - Generate all documentation formats"
	@echo "  update-metadata     - Update metadata (version, author, etc.) in files"

# # Setup environment
# .PHONY: setup
# setup:
# 	rm -rf $(VENV_DIR)
# 	python3 -m venv $(VENV_DIR)
# 	$(PIP) install -r $(REQ_FILE)

# .PHONY: setup-dev
# setup-dev:
# 	rm -rf $(VENV_DIR)
# 	python3 -m venv $(VENV_DIR)
# 	$(PIP) install -r $(DEV_REQ_FILE)

# # Clean up build, cache, and coverage files
# .PHONY: clean
# clean:
# 	rm -rf $(VENV_DIR) $(DOC_BUILD) build dist *.egg-info .pytest_cache __pycache__ src/__pycache__

# # Build project using hatch
# .PHONY: build
# build:
# 	hatch build

# # PyInstaller for packaging the project into a binary for Windows
# .PHONY: pyinstaller-package
# pyinstaller-package:
# 	$(VENV_DIR)/bin/pyinstaller --onefile src/cli.py

# # Run tests
# .PHONY: test
# test:
# 	$(VENV_DIR)/bin/pytest

# # Run tests and generate coverage report
# .PHONY: coverage
# coverage:
# 	$(VENV_DIR)/bin/pytest --cov=$(SRC) --cov-report=html --cov-report=term

# # Apply formatting with ruff
# .PHONY: format
# format:
# 	$(VENV_DIR)/bin/ruff --fix .

# # Run the project in a virtual environment
# .PHONY: run
# run:
# 	$(PYTHON) src/cli.py

# # Debugging with an environment variable set
# .PHONY: debug
# debug:
# 	DODEBUG=1 $(PYTHON) src/cli.py

# # Generate a changelog (assuming git is used)
# .PHONY: changelog
# changelog:
# 	git log --pretty=format:"%h %ad | %s%d [%an]" --date=short > CHANGELOG.md

# # Check for outdated dependencies
# .PHONY: deps
# deps:
# 	$(PIP) list --outdated

# # Generate HTML documentation
# .PHONY: docs-html
# docs-html:
# 	$(SPHINXBUILD) -b html $(DOC_SRC) $(DOC_BUILD)/html
# 	@echo "HTML documentation generated at $(DOC_BUILD)/html"

# # Generate PDF documentation (using LaTeX)
# .PHONY: docs-pdf
# docs-pdf:
# 	$(SPHINXBUILD) -b latex $(DOC_SRC) $(DOC_BUILD)/latex
# 	make -C $(DOC_BUILD)/latex all-pdf
# 	@echo "PDF documentation generated at $(DOC_BUILD)/latex"

# # Generate all documentation formats
# .PHONY: docs
# docs: docs-html docs-pdf
# 	@echo "All documentation formats generated."

# # Update metadata in files
# .PHONY: update-metadata
# update-metadata:
# 	$(SH) $(UPDATE_SCRIPT)
# 	@echo "Metadata updated in source files."
