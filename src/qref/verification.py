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

from collections import Counter, defaultdict
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from typing import Callable

from .functools import accepts_all_qref_types
from .schema_v1 import RoutineV1

Graph = dict[str, list[str]]


@dataclass
class TopologyVerificationOutput:
    """Dataclass containing the output of the topology verification"""

    problems: list[str]

    @property
    def is_valid(self):
        return len(self.problems) == 0

    def __bool__(self) -> bool:
        return self.is_valid


@accepts_all_qref_types
def verify_topology(routine: RoutineV1) -> TopologyVerificationOutput:
    """Checks whether program has correct topology.

    Correct topology cannot include cycles or disconnected ports.

    Args:
        routine: Routine or program to be verified.
    """
    problems = _verify_routine_topology(routine)
    return TopologyVerificationOutput(problems)


def _make_prefixer(ancestor_path: tuple[str, ...]) -> Callable[[str], str]:
    def _prefix(text: str) -> str:
        return ".".join([*ancestor_path, text])

    return _prefix


def _verify_routine_topology(routine: RoutineV1, ancestor_path: tuple[str, ...] = ()) -> list[str]:
    return [
        *_find_cycles(routine, ancestor_path),
        *_find_disconnected_ports(routine, ancestor_path),
        *[
            problem
            for child in routine.children
            for problem in _verify_routine_topology(child, ancestor_path + (routine.name,))
        ],
    ]


def _graph_from_routine(routine: RoutineV1, path: tuple[str, ...]) -> Graph:
    """Convert routine to a graph in a format expected by graphlib.

    Nodes represent ports and edges represent connections (they're directed).
    Additionaly, we add node for each children and edges coming from all the input ports
    into the children, and from the children into all the output ports.
    """
    graph = defaultdict[str, list[str]](list)
    _prefix = _make_prefixer(path + (routine.name,))

    # First, we go through all the connections and add them as adges to the graph
    for connection in routine.connections:
        source = _prefix(connection.source)
        target = _prefix(connection.target)
        graph[target].append(source)

    # Then for each children we add an extra node and set of connections
    for child in routine.children:
        input_ports: list[str] = []
        output_ports: list[str] = []

        child_path = _prefix(child.name)
        for port in child.ports:
            if port.direction == "input":
                input_ports.append(".".join([child_path, port.name]))
            elif port.direction == "output":
                output_ports.append(".".join([child_path, port.name]))

        for input_port in input_ports:
            graph[child_path].append(input_port)

        for output_port in output_ports:
            graph[output_port].append(child_path)

    return graph


def _find_cycles(routine: RoutineV1, ancestor_path: tuple[str, ...]) -> list[str]:
    sorter = TopologicalSorter(_graph_from_routine(routine, ancestor_path))
    try:
        _ = tuple(sorter.static_order())  # static_order is a generator, tuple() triggers actual iteration
    except CycleError as e:
        return [f"Cycle detected: {e.args[1]}"]

    return []


def _find_disconnected_ports(routine: RoutineV1, ancestor_path: tuple[str, ...]) -> list[str]:
    problems: list[str] = []

    _prefix = _make_prefixer(ancestor_path + (routine.name,))

    sources_counts = Counter[str]()
    target_counts = Counter[str]()

    for connection in routine.connections:
        sources_counts[connection.source] += 1
        target_counts[connection.target] += 1

    multi_sources = [source for source, count in sources_counts.items() if count > 1]

    multi_targets = [target for target, count in target_counts.items() if count > 1]

    if multi_sources:
        problems.append(f"Too many outgoing connections from {','.join(_prefix(target) for target in multi_sources)}.")

    if multi_targets:
        problems.append(f"Too many incoming connections to {','.join(_prefix(target) for target in multi_targets)}.")

    requiring_outgoing = set[str]()
    requiring_incoming = set[str]()
    thru_ports = set[str]()

    for port in routine.ports:
        if port.direction == "input" and routine.children:
            requiring_outgoing.add(port.name)
        elif port.direction == "output" and routine.children:
            requiring_incoming.add(port.name)
        elif port.direction == "through":  # Note: through ports have to be valid regardless of existence of children
            thru_ports.add(port.name)

    for child in routine.children:
        # Directions are reversed compared to parent + through ports have to be connected on both ends
        for port in child.ports:
            pname = f"{child.name}.{port.name}"
            if port.direction != "output":
                requiring_incoming.add(pname)
            if port.direction != "input":
                requiring_outgoing.add(pname)

    for pname in requiring_outgoing:
        if pname not in sources_counts:
            problems.append(f"No outgoing connection from {_prefix(pname)}.")

    for pname in requiring_incoming:
        if pname not in target_counts:
            problems.append(f"No incoming connection to {_prefix(pname)}.")

    for pname in thru_ports:
        if pname in sources_counts or pname in target_counts:
            problems.append(f"A through port {_prefix(pname)} is connected via an internal connection.")

    return problems
