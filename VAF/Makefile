include tests/Makefile

# To change the coverage (or any other set variable in the central Makefile) the include statement must occur after the overwritten variable, like this:
# fail verify:coverage job if branch coverage is below a specific value.
# default value: 100
# COV_FAIL_UNDER=87

# utility functions (OS dependent if necessary)
OS ?= $(shell uname)
PYTHON_VERSION ?= 3.12
ifeq ($(OS),Windows_NT)
	rm_if_exist = if exist $(1) rm -rf $(1)
endif
ifeq ($(OS),Linux)
	rm_if_exist = if [ -e $(1) ] ; then rm -rf $(1) ; fi ;
endif
rwildcard=$(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2) $(filter $(subst *,%,$2),$d))

start: clean upgrade
	uv sync --reinstall

upgrade:
	uv sync --upgrade

check-format:
	uv run --python ${PYTHON_VERSION} ruff format --check --diff

format: start
	uv run --python ${PYTHON_VERSION} ruff format
	uv run --python ${PYTHON_VERSION} ruff check --fix

lint:
	uv run --python ${PYTHON_VERSION} ruff check
	uv run --python ${PYTHON_VERSION} pylint src/
	uv run --python ${PYTHON_VERSION} pylint tests/
	uv run --python ${PYTHON_VERSION} mypy --install-types --non-interactive

build:
	uv build --python ${PYTHON_VERSION} --out-dir dist/

install:
	pip3 install --force-reinstall --break-system-packages --trusted-host pypi.org --trusted-host files.pythonhosted.org dist/*.whl

clean:
	@$(foreach path, $(call rwildcard, *, *.py[co]), $(call rm_if_exist, ${path}))
	@$(foreach path, $(call rwildcard, *, *__pycache__), $(call rm_if_exist, ${path}))
	@$(call rm_if_exist, __pypackages__)
	@$(call rm_if_exist, dist)
	@$(call rm_if_exist, report.xml)
	@$(call rm_if_exist, htmlcov)
	@$(call rm_if_exist, .pdm.toml)
	@$(call rm_if_exist, .pypy_cache)
	@$(call rm_if_exist, .pytest_cache)
	@$(call rm_if_exist, .mypy_cache)
	@$(call rm_if_exist, .coverage)
	@$(call rm_if_exist, .coverage*)
	@$(call rm_if_exist, .venv)
	@$(call rm_if_exist, .tox)
