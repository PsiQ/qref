# HQAR
Hierarchical Quantum Algorithms Representation is an open format for representing
quantum algorithms, optimized for usage in quantum resource estimation (QRE).

HQAR comprises:

- Definition of data format, formalized as a JSON schema.
- A Python library for validation of quantum programs written in HQAR format using [Pydantic](https://docs.pydantic.dev/).


## Installation

Using HQAR data format does not require installation - you can easily write quantum
programs in YAML or JSON.

To install HQAR Python package, clone this repository and install it as usual with `pip`:

```bash
# Clone HQAR repo (you can use HTTP link as well)
git clone git@github.com:PsiQ/hqar.git
cd hqar
pip install .
```

## HQAR format

Consider the following hierarchical dag a hypothetical quantum program:

![program example](example_routine.svg)

It can be succinctly written in HQAR format as:


```yaml
version: v1
program:
  name: my_algorithm
  ports:
  - direction: input
    name: in_0
    size: 2
  - direction: input
    name: in_1
    size: 2
  - direction: output
    name: out_0
    size: 4
  children:
  - name: subroutine_1
    ports:
    - direction: input
      name: in_0
      size: 2
    - direction: output
      name: out_0
      size: 3
  - name: subroutine_2
    ports:
    - direction: input
      name: in_0
      size: 2
    - direction: output
      name: out_0
      size: 1
    - direction: output
      name: out_1
      size: 1
  - name: merge
    ports:
    - direction: input
      name: in_0
      size: 1
    - direction: input
      name: in_1
      size: 1
    - direction: input
      name: in_2
      size: 2
    - direction: output
      name: out_0
      size: 4
  connections:
  - source: in_0
    target: subroutine_1.in_0
  - source: in_1
    target: subroutine_2.in_0
  - source: subroutine_1.out_0
    target: merge.in_2
  - source: subroutine_2.out_0
    target: merge.in_0
  - source: subroutine_2.out_1
    target: merge.in_1
  - source: merge.out_0
    target: out_0
```


For full description of HQAR format, check our [docs](https://example.com).

