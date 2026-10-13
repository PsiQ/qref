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
from subprocess import Popen
from xml.etree import ElementTree

import pytest

from qref import verify_topology
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


@pytest.mark.parametrize("through_names", [("q",), ("q", "r")])
@pytest.mark.parametrize("nested", [False, True])
def test_through_port_helpers_do_not_hide_real_ports(through_names, nested):
    def port(name, direction):
        return {"name": name, "direction": direction, "size": 1}

    inner = {"name": "inner", "ports": [], "children": [], "connections": []}
    worker_ports = []
    for name in through_names:
        inner["ports"].extend([port(name, "through"), port(name + "_in", "input"), port(name + "_out", "output")])
        worker_ports.append(port(name, "through"))
        inner["connections"].extend([name + "_in -> worker." + name, "worker." + name + " -> " + name + "_out"])
    inner["children"].append({"name": "worker", "ports": worker_ports})
    routine = inner
    if nested:
        routine = {"name": "outer", "ports": [], "children": [inner], "connections": []}
        for p in inner["ports"]:
            name = p["name"]
            if p["direction"] != "output":
                routine["ports"].append(port("in_" + name, "input"))
                routine["connections"].append("in_" + name + " -> inner." + name)
            if p["direction"] != "input":
                routine["ports"].append(port("out_" + name, "output"))
                routine["connections"].append("inner." + name + " -> out_" + name)

    assert verify_topology(routine)
    svg = ElementTree.fromstring(to_graphviz(routine).pipe(format="svg"))
    ns = {"svg": "http://www.w3.org/2000/svg"}
    nodes = svg.findall(".//svg:g[@class='node']", ns)
    labels = {label.text for node in nodes for label in node.findall("svg:text", ns)}
    for name in through_names:
        assert name in labels
        assert name + "_in" in labels
        assert name + "_out" in labels
