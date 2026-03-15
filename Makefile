# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

# Use bash even on Windows
SHELL := /bin/bash

PACKAGE_NAME = rapidyaml
PYPI_TEST_USER = jpmag
# PYPI_TEST = --repository-url https://test.pypi.org/legacy/
PYPI_TEST = --repository testpypi

# On Windows the activate script is stored in a different location.
ACTIVATE_SCRIPT := venv/bin/activate
ifeq ($(OS),Windows_NT)
ACTIVATE_SCRIPT := venv/Scripts/activate
endif

# How to invoke python
PYTHON := python
# How to invoke pytest
PYTEST := $(PYTHON) -m pytest -vvv -s

ACTIVATE = [[ -e $(ACTIVATE_SCRIPT) ]] && source $(ACTIVATE_SCRIPT);

.PHONY: all
all: build

.PHONY: upload-test
upload-test: $(ACTIVATE_SCRIPT)
	$(MAKE) clean
	$(MAKE) build-sdist
	${ACTIVATE} twine upload ${PYPI_TEST} dist/*

.PHONY: upload
upload: $(ACTIVATE_SCRIPT)
	$(MAKE) clean
	$(MAKE) build-sdist
	${ACTIVATE} twine upload --verbose dist/*

# testpypi accumulates test releases and regularly reaches the 10GB
# size limit; use this target to clear the test releases
# see:
#   https://pypi.org/project/pypi-cleanup/
.PHONY: clear_testpypi
clear-testpypi: $(ACTIVATE_SCRIPT)
	${ACTIVATE} pypi-cleanup -t https://test.pypi.org -u $(PYPI_TEST_USER) -p $(PACKAGE_NAME) --leave-most-recent-only --do-it --yes

.PHONY: clean
clean:
	rm -rvf dist *.egg-info
	rm -rvf build .egg*
	rm -rvf ryml/*.so ryml/ryml.py ryml/include ryml/lib

.PHONY: venv-clean
venv-clean:
	rm -rf venv


$(ACTIVATE_SCRIPT): requirements.txt Makefile
	make venv
	@touch $(ACTIVATE_SCRIPT)

.PHONY: venv
venv:
	virtualenv --python=python3 --always-copy venv
	# Packaging tooling.
	${ACTIVATE} pip install -U pip
	# Setup requirements.
	${ACTIVATE} pip install -v -r requirements.txt

.PHONY: build-sdist
build-sdist: | $(ACTIVATE_SCRIPT)
	${ACTIVATE} pip show build
	${ACTIVATE} $(PYTHON) -m build --sdist --outdir $(PWD)/dist


.PHONY: build-wheel
build-wheel: | $(ACTIVATE_SCRIPT)
	rm -rf dist
	$(MAKE) build-sdist
	@ls -l dist/*.tar.gz
	${ACTIVATE} pip wheel -v dist/*.tar.gz --wheel-dir $(PWD)/dist

.PHONY: build
build: build-sdist build-wheel

.PHONY: check
check: | $(ACTIVATE_SCRIPT)
	$(MAKE) clean
	$(MAKE) build-wheel
	${ACTIVATE} twine check dist/*.whl

.PHONY: install
install: | $(ACTIVATE_SCRIPT)
	${ACTIVATE} $(PYTHON) setup.py install

.PHONY: test
test: | $(ACTIVATE_SCRIPT)
	${ACTIVATE} pip install -v -e .
	${ACTIVATE} $(PYTHON) -c "from ryml.version import version as v; print('Installed version:', v)"
	${ACTIVATE} $(PYTEST) test

.PHONY: version
version: | $(ACTIVATE_SCRIPT)
	${ACTIVATE} $(PYTHON) setup.py --version
