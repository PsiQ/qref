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

You can also develop Poetry using `pip`:

```bash
pip install -e .
```

!!! Warning

    If you are planning to add/modify dependencies of QREF, we
    highly recommend you use Poetry instead of pip editable install.
    Without Poetry, you will need to edit dependencies manually,
    which is very error-prone.
