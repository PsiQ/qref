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

"""Experimental visualization capabilities for QREF.

Currently, the visualizations are done with graphviz, which does not suport
hierarchical structures. Therefore, we have to use a somewhat hacky representation
of our routines:

- The leaf nodes are drawn as a single graphviz node (this is not surprising) with
  Mrecord shape. This allows to visually separate routine name from its ports.
- The non-leaf nodes are represented as clusters.
  - Clusters can't use Mrecord shape, and so the ports are drawn as separate nodes.
  - Input and output ports are grouped into subgraphs with the same rank, which
    forces all inputs / all outputs to be placed in a single column.

Because of the above dichotomy, care has to be taken when constructing edges.
- If addressing port of a leaf, it must be specified as graphviz port, e.g:
  "root.child:in_0"
- If addressing port of a non-leaf, you use normal node reference, e.g:
  "root.child.in_0"
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Union

import graphviz
import yaml

from .. import SchemaV1

# Dictionary of default graph attributes, used for non-leaf nodes
GRAPH_ATTRS = {
    "rankdir": "LR",  # Draw left to right (default is top to bottom)
    "fontname": "Helvetica",
}

# Keyword args passed to dag.node for drawing leaf nodes
LEAF_NODE_KWARGS = {
    "shape": "Mrecord",  # Allow drawing leafs split into labels/ports
    "style": "bold",  # Bold border
    "color": "#0288f5",  # Nice blue color
    "fontsize": "12",  # Larger font size then e.g. ports of non-leafs
}

# Keyword args passed to dag.node for drawing ports of non-leaf nodes
PORT_NODE_KWARGS = {
    "style": "bold",  # Bold border
    "color": "#ffa44a",  # Orange border color
    "fontsize": "10",  # Smaller font size than the rest of the graph
    "shape": "circle",
}

# Additional attributes of subgraphs of ports (ports of the same direction
# are grouped into such subgraphs)
PORT_GROUP_ATTRS = {"rank": "same"}  # Place all ports in the group in the same column

# Additional kwargs passed to dag.subgraph for defining non-leaf clusters
CLUSTER_KWARGS = {"style": "rounded"}  # Make cluster edges rounded


def _format_node_name(node_name, parent):
    """Given a node name and a parent container, format it accordingly.

    Read the module-level docstring for explanation why different port formats
    of ports are being used.
    """
    if "." not in node_name:  # Case 1: parent port (=> port is a graphviz node)
        return node_name

    # Resolve the child, assume the graph is correct and thus the child exists.
    child_name, port_name = node_name.split(".")
    child = next(iter((child for child in parent.children if child.name == child_name)))
    if child.children:  # Case 2: port of non-leaf child (=> port is a graphviz node)
        return node_name
    else:  # Case 3: port of leaf child (=> port is an actual port of Mrecord, use ":")
        return f"{child_name}: {port_name}"


def _add_nonleaf_ports(ports, parent_cluster, parent_path: str, group_name):
    with parent_cluster.subgraph(name=f"{parent_path}: {group_name}", graph_attr=PORT_GROUP_ATTRS) as subgraph:
        for port in ports:
            subgraph.node(name=f"{parent_path}.{port.name}", label=port.name, **PORT_NODE_KWARGS)


def _split_ports(ports):
    input_ports = []
    output_ports = []
    for port in ports:
        if port.direction == "input":
            input_ports.append(port)
        elif port.direction == "output":
            output_ports.append(port)
        else:
            raise ValueError("Bi-directional ports are not yet supported for rendering")
    return input_ports, output_ports


def _add_nonleaf(routine, dag: graphviz.Digraph, parent_path: str) -> None:
    input_ports, output_ports = _split_ports(routine.ports)
    full_path = f"{parent_path}.{routine.name}"

    with dag.subgraph(name=f"cluster_{full_path}", graph_attr={"label": routine.name, **CLUSTER_KWARGS}) as cluster:
        _add_nonleaf_ports(input_ports, cluster, full_path, "inputs")
        _add_nonleaf_ports(output_ports, cluster, full_path, "outputs")

        for child in routine.children:
            _add_routine(child, cluster, f"{parent_path}.{routine.name}")

        for connection in routine.connections:
            cluster.edge(
                full_path + "." + _format_node_name(connection.source, routine),
                full_path + "." + _format_node_name(connection.target, routine),
            )


def _ports_row(ports) -> str:
    return "{" + "|".join(f"<{port.name}> {port.name}" for port in ports) + "}"


def _add_leaf(routine, dag: graphviz.Digraph, parent_path: str) -> None:
    input_ports, output_ports = _split_ports(routine.ports)
    label = f"{{{_ports_row(input_ports)}|{routine.name}|{_ports_row(output_ports)}}}"
    dag.node(".".join((parent_path, routine.name)), label=label, **LEAF_NODE_KWARGS)


def _add_routine(routine, dag: graphviz.Digraph, parent_path: str = "") -> None:
    if routine.children:
        _add_nonleaf(routine, dag, parent_path)
    else:
        _add_leaf(routine, dag, parent_path)


def _ensure_schema_v1(data: Union[dict, SchemaV1]) -> SchemaV1:
    return data if isinstance(data, SchemaV1) else SchemaV1(**data)


def to_graphviz(data: Union[dict, SchemaV1]) -> graphviz.Digraph:
    """Convert routine encoded with v1 schema to a graphviz DAG."""
    data = _ensure_schema_v1(data)
    dag = graphviz.Digraph(graph_attr=GRAPH_ATTRS)
    _add_routine(data.program, dag)
    return dag


def render_entry_point():
    parser = ArgumentParser()
    parser.add_argument("input", help="Path to the YAML or JSON file with Routine in V1 schema", type=Path)
    parser.add_argument(
        "output",
        help=(
            "Path to the output file. File format is determined based on the extension, "
            "which should be either .svg or .pdf"
        ),
        type=Path,
    )

    args = parser.parse_args()

    with open(args.input) as f:
        routine = SchemaV1.model_validate(yaml.safe_load(f))

    dag = to_graphviz(routine)
    dag.render(args.output.with_suffix(""), format=args.output.suffix.strip("."))
