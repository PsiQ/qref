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

from collections import defaultdict
from dataclasses import dataclass
from typing import Union

from ._schema_v1 import RoutineV1, SchemaV1


@dataclass
class TopologyVerificationOutput:
    """Dataclass containing the output of the topology verification"""

    is_valid: bool
    problems: list[str]

    def __bool__(self) -> bool:
        return self.is_valid


def verify_topology(routine: Union[SchemaV1, RoutineV1]) -> TopologyVerificationOutput:
    """Checks whether program has correct topology.

    Args:
        routine: Routine or program to be verified.
    """
    if isinstance(routine, SchemaV1):
        routine = routine.program
    problems = _verify_routine_topology(routine, is_root=True)
    if problems:
        return TopologyVerificationOutput(False, problems)
    else:
        return TopologyVerificationOutput(True, problems)


def _verify_routine_topology(routine: RoutineV1, is_root: bool) -> list[str]:
    problems = []
    flat_graph = _get_flat_graph_from_routine(routine, path=None)
    edge_list = []
    for source, targets in flat_graph.items():
        edge_list += [(source, target) for target in targets]

    problems += _find_cycles(flat_graph)
    problems += _find_disconnected_ports(routine, is_root)

    for child in routine.children:
        new_problems = _verify_routine_topology(child, is_root=False)
        if new_problems:
            problems += new_problems
    return problems


def _get_flat_graph_from_routine(routine, path) -> dict[str, list[str]]:
    graph = defaultdict(list)
    if path is None:
        current_path = routine.name
    else:
        current_path = ".".join([path, routine.name])

    input_ports = []
    output_ports = []

    for port in routine.ports:
        if port.direction == "input":
            input_ports.append(".".join([current_path, port.name]))
        elif port.direction == "output":
            output_ports.append(".".join([current_path, port.name]))

    for connection in routine.connections:
        source = ".".join([current_path, connection.source])
        target = ".".join([current_path, connection.target])
        graph[source].append(target)

    for child in routine.children:
        input_ports = []
        output_ports = []

        child_path = ".".join([current_path, child.name])
        for port in child.ports:
            if port.direction == "input":
                input_ports.append(".".join([child_path, port.name]))
            elif port.direction == "output":
                output_ports.append(".".join([child_path, port.name]))

        for input_port in input_ports:
            graph[input_port].append(child_path)

        graph[child_path] += output_ports

    return graph


def _find_cycles(edges) -> list[str]:
    for node in list(edges.keys()):
        visited: list[str] = []
        problem = _dfs_iteration(edges, node, node, visited)
        if problem:
            return problem
    return []


def _dfs_iteration(edges, initial_node, node, visited):
    if node != initial_node:
        visited.append(node)
    for neighbour in edges[node]:
        if neighbour not in visited:
            if neighbour == initial_node:
                return [f"Cycle detected for node: {node}. Cycle: {visited}."]
            problem = _dfs_iteration(edges, initial_node, neighbour, visited)
            if problem:
                return problem


def _find_disconnected_ports(routine: RoutineV1, is_root: bool):
    problems = []
    conns = [c.model_dump() for c in routine.connections]
    for child in routine.children:
        for port in child.ports:
            pname = f"{routine.name}.{child.name}.{port.name}"
            if port.direction == "input":
                matches_in = [c for c in conns if c["target"] == f"{child.name}.{port.name}"]
                if len(matches_in) == 0:
                    problems.append(f"No incoming connections to {pname}.")
                elif len(matches_in) > 1:
                    problems.append(f"Too many incoming connections to {pname}.")
            elif port.direction == "output":
                matches_out = [c for c in conns if c["source"] == f"{child.name}.{port.name}"]
                if len(matches_out) == 0:
                    problems.append(f"No outgoing connections from {pname}.")
                elif len(matches_out) > 1:
                    problems.append(f"Too many outgoing connections from {pname}.")

    return problems
