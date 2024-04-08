# User guide

## Installation

To install QART Python package, clone QARt repository and install it as usual with `pip`:

```bash
# Clone QART repo (you can use HTTP link as well)
git clone git@github.com:PsiQ/qart.git
cd qart
pip install .
```

Please note that to use rendering features you need a working [graphviz](https://graphviz.org)
installation.

## Usage


### Using JSON schema for validating data in QART format

JSON schema for QART format can be obtained by calling
[`generate_program_schema`][qart.generate_program_schema] function.
Such schema can be then used for validating user's input, e.g. using
[`jsonschema`](https://pypi.org/project/jsonschema/) package:

```python
from jsonschema import validate
from qart import generate_program_schema

# Hypothetical function loading your data as native Python dictionary.
data = load_some_program()
schema = generate_program_schema()

# This will raise if there are some validation errors.
validate(schema, data)
```

### Validation using Pydantic models

If you are familiar with [Pydantic](https://docs.pydantic.dev/latest/), you might find
it easier to work with QART Pydantic models instead of interacting with JSON schema directly.
In the example below, we create an instance of [`SchemaV1`][qart.SchemaV1] model from
validated data stored in QART format:

```python
from qart import SchemaV1

data = load_some_program()

# This will raise if data is not valid
program = SchemaV1.model_validate(data)
```

### Rendering QART files using `qart-render` (experimental)

!!! Warning

    This feature is considered experimental and may occassionally produce
    incorrect results.


QART comes with a CLI tool for rendering hierarchical graphs of quantum
algorithms. To render an algorithm stored in a file named `my_program.yaml` into a 
file `my_program_graph.svg` run:

```bash
qart-render my_program.yaml my_program_graph.svg
```

The `qart-render` tool supports `yaml` and `json` input formats, and all
output formats supported by [graphviz](https://graphviz.org/).

If, instead of using CLI, you'd like to invoke QART's rendering capabilities
from Python script, you can look at [qart.experimental.rendering][qart.experimental.rendering]
module which exposes experimental API for performing the same task as `qart-render`.


