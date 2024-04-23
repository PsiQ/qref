"""Sanity checks for QREF rendering capabilities."""

import json
from subprocess import Popen

from qref.experimental.rendering import to_graphviz


def test_example_valid_programs_can_converted_to_graphviz(valid_program):
    to_graphviz(valid_program)


def test_example_valid_programs_can_be_rendered_from_cli(valid_program, tmp_path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.svg"

    with open(input_path, "wt") as f:
        json.dump(valid_program, f)

    process = Popen(["qref-render", input_path, output_path])
    process.wait()

    assert process.returncode == 0
