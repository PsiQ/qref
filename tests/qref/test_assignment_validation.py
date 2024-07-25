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
import pytest
from pydantic import ValidationError

from qref.schema_v1 import PortV1, ResourceV1, RoutineV1


@pytest.fixture
def example_routine():
    return RoutineV1.model_validate(
        {
            "name": "root",
            "children": [
                {
                    "name": "a",
                    "ports": [
                        {"name": "ctrl", "size": "N", "direction": "input"},
                        {"name": "target", "size": "N", "direction": "input"},
                        {"name": "out", "size": "2N", "direction": "output"},
                    ],
                },
                {"name": "b"},
            ],
            "ports": [
                {"name": "in_0", "size": 2, "direction": "input"},
                {"name": "out_0", "size": 3, "direction": "output"},
            ],
            "resources": [
                {"name": "n_rotations", "value": 4, "type": "additive"},
                {"name": "n_toffs", "value": 100, "type": "additive"},
            ],
            "connections": ["in_0 -> a.ctrl"],
        }
    )


def test_setting_children_list_to_a_list_of_dictionaries_gives_a_list_of_routines(example_routine):
    example_routine.children = [
        {"name": "a", "ports": [{"name": "ctrl", "size": "N", "direction": "input"}]},
        {"name": "c"},
        {"name": "d"},
    ]

    assert all(isinstance(child, RoutineV1) for child in example_routine.children)


def test_setting_children_list_to_an_incorrect_dictionary_raises_validation_error(example_routine):
    with pytest.raises(ValidationError):
        # The assignment here is invalid because we are left with connection to a.in_0, which
        # will cease to exist after the assignment.
        example_routine.children = [
            {"name": "a", "ports": [{"name": "in_0", "size": "N", "direction": "input"}]},
            {"name": "c"},
            {"name": "d"},
        ]


def test_setting_ports_list_to_a_list_of_dictionaries_gives_a_list_of_ports(example_routine):
    example_routine.ports = [
        {"name": "in_0", "size": 2, "direction": "input"},
    ]

    assert len(example_routine.ports) == 1 and isinstance(example_routine.ports[0], PortV1)


def test_setting_port_list_to_an_incorrect_value_raises_validation_error(example_routine):
    with pytest.raises(ValidationError):
        example_routine.ports = [{"name": "out_0", "size": 3, "direction": "output"}]


def test_setting_resources_to_a_list_of_dictionaries_gives_a_list_of_resources_v1(example_routine):
    example_routine.resources = [
        {"name": "n_rotations", "value": 40, "type": "additive"},
        {"name": "n_toffs", "value": 10, "type": "additive"},
    ]

    assert all(isinstance(resource, ResourceV1) for resource in example_routine.resources)

    assert example_routine.resources.by_name["n_rotations"].value == 40
    assert example_routine.resources.by_name["n_toffs"].value == 10


def test_setting_resources_to_an_incorrect_value_raies_validation_error(example_routine):
    with pytest.raises(ValidationError):
        example_routine.resources = [{"name": "n_toffs", "quantity": "N"}]


def test_setting_connections_to_a_new_value_converts_it_to_list_of_connection_v1(example_routine):
    example_routine.connections = ["in_0 -> a.target"]

    assert len(example_routine.connections) == 1

    connection = example_routine.connections[0]

    assert (connection.source, connection.target) == ("in_0", "a.target")


def test_setting_connections_to_incorrect_value_raises_validation_error(example_routine):
    with pytest.raises(ValidationError):
        # Incorrect, since there is no b.in_0 port
        example_routine.connections = ["in_0 -> b.in_0"]
