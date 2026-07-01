fmt: fmt-ruff lint-ruff-fix

lint: lint-ruff lint-pyrefly

test: test-pytest

run: run-pymushra

fmt-ruff:
    uv run ruff format

lint-ruff:
    uv run ruff check

lint-ruff-fix:
    uv run ruff check --fix

lint-pyrefly:
    uv run pyrefly check

test-pytest:
    uv run pytest

run-pymushra:
    uv run pymushra server
