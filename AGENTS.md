# AGENTS.md

## Repo purpose

`qref` defines the Quantum Resource Estimation Format and provides validation, schema tooling, docs, and rendering utilities.

## Setup prerequisites

- Python 3.10-3.12
- `poetry`
- Graphviz on `PATH` for rendering-related workflows

## Canonical local commands

- Install default environment: `poetry install`
- Install docs environment: `poetry install --with docs`
- Lint/hooks: `pre-commit run -a`
- Unit tests: `poetry run pytest --json-report --json-report-file=pytest_report.json --json-report-omit collectors log streams --cov src --cov-report term --cov-report html`
- Type checks: `MYPYPATH=src poetry run mypy src --install-types --non-interactive`
- Docs build: `poetry run mkdocs build`

## Validation before handoff

- Run `pre-commit run -a` for normal code changes.
- Run the pytest command for library or schema changes.
- Run the mypy command when changing typed library code.
- Run `poetry run mkdocs build` when touching docs or `mkdocs.yml`.

## Risky or restricted areas

- Keep GitHub Actions and release automation aligned with the existing GitHub workflow model.
- Schema or validation changes can affect downstream consumers broadly.
- Graphviz-dependent rendering paths may fail without the system binary.

## Repo-specific notes for agents

- This repo uses GitHub Actions and an open-source-style workflow rather than the internal GitLab conventions used by most other repos here.
- Pre-commit uses `isort`, `black`, and `flake8`, not Ruff.
- Preserve compatibility expectations for the QREF format unless the task explicitly changes schema behavior.
