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
                    ],
                },
                {"name": "b", "children": [{"name": "c"}]},
            ],
            "ports": [
                {"name": "in_0", "size": 2, "direction": "input"},
                {"name": "out_0", "size": 3, "direction": "output"},
            ],
            "resources": [
                {"name": "n_rotations", "value": 4, "type": "additive"},
                {"name": "n_toffs", "value": 100, "type": "additive"},
            ],
        }
    )


class TestAccessingChildrenByName:
    def test_can_get_direct_child_by_name(self, example_routine):
        assert example_routine.children.by_name["a"] == example_routine.children[0]

    def test_can_get_nested_child_by_name(self, example_routine):
        assert example_routine.children.by_name["b"].children.by_name["c"] == example_routine.children[1].children[0]

    def test_can_set_child_by_name(self, example_routine):
        new_child = RoutineV1(name="b")
        example_routine.children.by_name["b"] = new_child

        assert example_routine.children[1] == new_child
        assert example_routine.children.by_name["b"] == new_child

    def test_can_delete_child_by_name(self, example_routine):
        del example_routine.children.by_name["b"]

        assert [child.name for child in example_routine.children] == ["a"]

    def test_trying_to_get_nonexisting_child_raises_key_error(self, example_routine):
        with pytest.raises(KeyError) as exc_info:
            _ = example_routine.children.by_name["x"]

        assert exc_info.value.args == ("x",)

    def test_nonexistent_child_cannot_be_set(self, example_routine):
        with pytest.raises(KeyError) as exc_info:
            new_child = RoutineV1(name="x")
            example_routine.children.by_name["x"] = new_child

        assert exc_info.value.args == ("x",)


class TestAccessingPortsByName:
    def test_can_get_port_by_name(self, example_routine):
        assert example_routine.ports.by_name["in_0"] == example_routine.ports[0]

    def test_can_set_port_by_name(self, example_routine):
        new_port = PortV1(name="ctrl", direction="input", size=10)
        example_routine.children[0].ports.by_name["ctrl"] = new_port

        assert example_routine.children[0].ports[0] == new_port

    def test_can_delete_port_by_name(self, example_routine):
        del example_routine.ports.by_name["out_0"]

        assert [port.name for port in example_routine.ports] == ["in_0"]

    def test_trying_to_get_nonexisting_port_raises_key_error(self, example_routine):
        with pytest.raises(KeyError) as exc_info:
            _ = example_routine.ports.by_name["in_10"]

        assert exc_info.value.args == ("in_10",)

    def test_nonexistent_port_cannot_be_set(self, example_routine):
        with pytest.raises(KeyError) as exc_info:
            new_port = PortV1(name="in_10", size=42, direction="input")
            example_routine.children.by_name["in_10"] = new_port

        assert exc_info.value.args == ("in_10",)


class TestAccessingResourcesByName:
    def test_can_get_resource_by_name(self, example_routine):
        assert example_routine.resources.by_name["n_toffs"] == example_routine.resources[1]

    def test_can_set_resource_by_name(self, example_routine):
        new_resource = ResourceV1(name="n_toffs", value=10, type="multiplicative")
        example_routine.resources.by_name["n_toffs"] = new_resource

        assert example_routine.resources[1] == new_resource

    def test_can_delete_resource_by_name(self, example_routine):
        del example_routine.resources.by_name["n_toffs"]

        assert [resource.name for resource in example_routine.resources] == ["n_rotations"]

    def test_trying_to_get_nonexisting_resource_raises_key_error(self, example_routine):
        with pytest.raises(KeyError) as exc_info:
            _ = example_routine.resources.by_name["n_qubits"]

        assert exc_info.value.args == ("n_qubits",)

    def test_nonexistent_resource_cannot_be_set(self, example_routine):
        with pytest.raises(KeyError) as exc_info:
            new_resource = ResourceV1(name="n_qubits", value=42, type="other")
            example_routine.resources.by_name["n_qubits"] = new_resource

        assert exc_info.value.args == ("n_qubits",)
