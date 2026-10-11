# Copyright 2024 PsiQuantum, Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from subprocess import Popen, run

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


def test_rendered_connections_use_declared_leaf_ports():
    routine = {
        "name": "root",
        "ports": [
            {"name": "in_0", "direction": "input", "size": 1},
            {"name": "in_1", "direction": "input", "size": 1},
            {"name": "out_0", "direction": "output", "size": 1},
            {"name": "out_1", "direction": "output", "size": 1},
        ],
        "children": [
            {
                "name": "operation",
                "ports": [
                    {"name": "in_0", "direction": "input", "size": 1},
                    {"name": "in_1", "direction": "input", "size": 1},
                    {"name": "out_0", "direction": "output", "size": 1},
                    {"name": "out_1", "direction": "output", "size": 1},
                ],
            }
        ],
        "connections": [
            "in_0 -> operation.in_0",
            "in_1 -> operation.in_1",
            "operation.out_0 -> out_0",
            "operation.out_1 -> out_1",
        ],
    }
    dag = to_graphviz(routine)

    process = run(["dot", "-Tsvg"], input=dag.source, text=True, capture_output=True, check=True)

    assert "unrecognized" not in process.stderr
