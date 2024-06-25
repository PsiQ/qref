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
from typing import Optional, Union

from .schema_v1 import RoutineV1, SchemaV1


@dataclass
class TopologyVerificationOutput:
    """Dataclass containing the output of the topology verification"""

    problems: list[str]

    @property
    def is_valid(self):
        return len(self.problems) == 0

    def __bool__(self) -> bool:
        return self.is_valid


def verify_topology(routine: Union[SchemaV1, RoutineV1]) -> TopologyVerificationOutput:
    """Checks whether program has correct topology.

    Correct topology cannot include cycles or disconnected ports.

    Args:
        routine: Routine or program to be verified.
    """
    if isinstance(routine, SchemaV1):
        routine = routine.program
    problems = _verify_routine_topology(routine)
    return TopologyVerificationOutput(problems)


def _verify_routine_topology(routine: RoutineV1) -> list[str]:
    problems = []
    adjacency_list = _get_adjacency_list_from_routine(routine, path=None)

    problems += _find_cycles(adjacency_list)
    problems += _find_disconnected_ports(routine)

    for child in routine.children:
        new_problems = _verify_routine_topology(child)
        problems += new_problems
    return problems


def _get_adjacency_list_from_routine(routine: RoutineV1, path: Optional[str]) -> dict[str, list[str]]:
    """This function creates a flat graph representing one hierarchy level of a routine.

    Nodes represent ports and edges represent connections (they're directed).
    Additionaly, we add node for each children and edges coming from all the input ports
    into the children, and from the children into all the output ports.
    """
    graph = defaultdict(list)
    if path is None:
        current_path = routine.name
    else:
        current_path = ".".join([path, routine.name])

    # First, we go through all the connections and add them as adges to the graph
    for connection in routine.connections:
        source = ".".join([current_path, connection.source])
        target = ".".join([current_path, connection.target])
        graph[source].append(target)

    # Then for each children we add an extra node and set of connections
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


def _find_cycles(adjacency_list: dict[str, list[str]]) -> list[str]:
    # Note: it only returns the first detected cycle.
    for node in list(adjacency_list.keys()):
        problem = _dfs_iteration(adjacency_list, node)
        if problem:
            return problem
    return []


def _dfs_iteration(adjacency_list, start_node) -> list[str]:
    to_visit = [start_node]
    visited = []
    predecessors = {}

    while to_visit:
        node = to_visit.pop()
        visited.append(node)
        for neighbour in adjacency_list[node]:
            predecessors[neighbour] = node
            if neighbour == start_node:
                # Reconstruct the cycle
                cycle = [neighbour]
                while len(cycle) < 2 or cycle[-1] != start_node:
                    cycle.append(predecessors[cycle[-1]])
                return [f"Cycle detected: {cycle[::-1]}"]
            if neighbour not in visited:
                to_visit.append(neighbour)
    return []


def _find_disconnected_ports(routine: RoutineV1):
    problems = []
    for child in routine.children:
        for port in child.ports:
            pname = f"{routine.name}.{child.name}.{port.name}"
            if port.direction == "input":
                matches_in = [c for c in routine.connections if c.target == f"{child.name}.{port.name}"]
                if len(matches_in) == 0:
                    problems.append(f"No incoming connections to {pname}.")
                elif len(matches_in) > 1:
                    problems.append(f"Too many incoming connections to {pname}.")
            elif port.direction == "output":
                matches_out = [c for c in routine.connections if c.source == f"{child.name}.{port.name}"]
                if len(matches_out) == 0:
                    problems.append(f"No outgoing connections from {pname}.")
                elif len(matches_out) > 1:
                    problems.append(f"Too many outgoing connections from {pname}.")

    return problems
