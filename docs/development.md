# Development guide

## Setting up development environment

QREF uses [Poetry](https://python-poetry.org/) for managing dependencies.
Therefore, we recommend you use Poetry to setup your environment. However,
if you insist on not using Poetry, the more traditional way of using
editable install with `pip` is still avaiable.

### Using editable install with Poetry

To setup your development environment install poetry (if you don't have it yet):

```bash
pip install poetry
```

And then install the project and its dependencies:

```bash
poetry install
```

### Using editable install with pip

If you prefer to manage your own environment, you can install an editable version of QREF via `pip`:

```bash
pip install -e .
```

!!! Warning

    If you are planning to add or modify the dependencies of QREF, we
    highly recommend you use Poetry instead of pip editable install.
    Without Poetry, you will need to edit dependencies manually,
    which is very error-prone.

### Development Standards
We use `pre-commit` hooks to ensure consistent development standards are maintained, and encourage any contributors to ensure `pre-commit` is installed prior to committing any changes to your branch. You can read the `pre-commit` docs [here](https://pre-commit.com).

`pre-commit` is installed as a dev dependency in QREF, but prior to committing any changes you must run:
```bash
poetry run pre-commit install
```
To run all `pre-commit` hooks locally:
```bash
poetry run pre-commit run --all
```
This command will print a summary of the current code quality in your branch.

!!!warning
    If using Visual Studio Code, the `git` integration in Source Control does not detect `pre-commit` hooks. To use these, `git` commands must be run through the terminal in the installed `qref` virtual environment.

## Setting up docs locally

In order to set up docs locally you need to have the appropriate dependencies – they get installed when running `poetry install` automatically. When done, please run:

```bash
mkdocs serve
```

