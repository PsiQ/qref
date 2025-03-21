# User guide

## Installation

To install the QREF Python package, clone the repository and install it with `pip`:

```bash
# Clone QREF repo (you can use HTTP link as well)
git clone git@github.com:PsiQ/qref.git
cd qref
pip install .
```

Please note that to use the rendering features you need a working [graphviz](https://graphviz.org)
installation.

## Data Validation

### Using JSON schema for data validation

A JSON schema for QREF can be obtained by calling
[`generate_program_schema`][qref.generate_program_schema].
This schema can be then used for validating user input, e.g. using
[`jsonschema`](https://pypi.org/project/jsonschema/) package:

```python
from jsonschema import validate
from qref import generate_program_schema

# Hypothetical function loading your data as native Python dictionary.
data = load_some_program()
schema = generate_program_schema()

# This will raise an exception if there are some validation errors.
validate(schema, data)
```

### Validation using Pydantic models

If you are familiar with [Pydantic](https://docs.pydantic.dev/latest/), you might find
it easier to work with QREF pydantic models instead of interacting with JSON schema directly.
In the example below, we create an instance of the [`SchemaV1`][qref.SchemaV1] model from data stored in QREF:

```python
from qref import SchemaV1

data = load_some_program()

# This will raise an exception if there are some validation errors.
program = SchemaV1.model_validate(data)
```

One of the benefits of using QREF's pydantic models is ability to obtain objects like children, ports
or resources by name, instead of list indices. This is done by special `.by_name` accessor. For instance
to get a child named `"foo"` of a `routine` object, one can use the following syntax:

```python
foo = routine.children.by_name["foo"]
```


### Topology validation

There can be cases where a program is correct from the perspective of Pydantic validation, but has incorrect topology. This includes cases such as:

- Disconnected ports
- Ports with multiple connections
- Cycles in the graph

In order to validate whether the topology of the program is correct you can use `verify_topology` method. Here's a short snippet showing how you can verify your program and print out the problems (if any).

```python
from qref.verification import verify_topology

program = load_some_program()

verification_output = verify_topology(program)

if not verification_output:
    print("Program topology is incorrect, due to the following issues:")
    for problem in verification_output.problems:
        print(problem)

```

### Rendering QREF files using `qref-render` (experimental)

!!! Warning
    This feature is considered experimental and may occassionally produce
    incorrect results.


QREF comes with a CLI tool for rendering hierarchical graphs of quantum
algorithms. To render an algorithm stored in a file named `my_program.yaml` into a 
file `my_program_graph.svg` run:

```bash
qref-render my_program.yaml my_program_graph.svg
```

The `qref-render` tool supports `yaml` and `json` input formats, and all
output formats supported by [graphviz](https://graphviz.org/).

If you prefer to use QREF's rendering capabilities from a Python script instead of the CLI, you can use the [`qref.experimental.rendering`](qref.experimental.rendering) module,  which performs the same task as `qref-render`. 

Below we demonstate how the rendering module visualizes the quantum circuit for arbitrary state preparation in the alias sampling algorithm. This algorithm is explored in detailed in the tutorials for [Bartiq](https://psiq.github.io/bartiq/latest/tutorials/02_alias_sampling_basic/) – our library for symbolic resource estimation.

We will use the `yaml` file `alias_sampling.yaml` as input to generate a graph representing this algorithm:

```python
import yaml
from qref import SchemaV1
from qref.experimental.rendering import to_graphviz

# Load the YAML file
with open("../examples/alias_sampling.yaml", "r") as f:
    data = yaml.safe_load(f)

# Validate the schema and convert to Graphviz object
program = SchemaV1.model_validate(data)
gv_object = to_graphviz(program)

# Render the Graphviz object to a PNG file
gv_object.render("alias_sampling", format="png")
```
![alias_sampling|500](../images/as.png)
