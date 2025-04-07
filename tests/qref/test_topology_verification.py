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

from pathlib import Path

import pytest
import yaml

from qref import SchemaV1
from qref.verification import verify_topology


def load_invalid_examples():
    with open(Path(__file__).parent / "data/invalid_topology_programs.yaml") as f:
        data = yaml.safe_load(f)

    return [
        pytest.param(
            example["input"],
            example["problems"],
            id=example["description"],
        )
        for example in data
    ]


def test_correct_routines_pass_topology_validation(valid_program):
    verification_output = verify_topology(SchemaV1(**valid_program))
    assert verification_output
    assert len(verification_output.problems) == 0


@pytest.mark.parametrize("input, problems", load_invalid_examples())
def test_invalid_program_fails_to_validate_with_schema_v1(input, problems):
    verification_output = verify_topology(SchemaV1(**input))

    # We use sorted here, to make sure that we don't test the order in which the
    # problems appear, as the order is only an implementation detail.
    assert sorted(verification_output.problems) == sorted(problems)


@pytest.mark.timeout(10)
def test_topology_verification_of_a_large_routine_completes_in_acceptable_time():
    N_CHILDREN = 10000

    qref_obj = {
        "version": "v1",
        "program": {
            "name": "test",
            "ports": [
                {"name": "in_0", "direction": "input", "size": 1},
                {"name": "out_0", "direction": "output", "size": 1},
            ],
            "children": [
                {"name": f"child_{i}", "ports": [{"name": "thru_0", "direction": "through", "size": 1}]}
                for i in range(N_CHILDREN)
            ],
            "connections": [
                "in_0 -> child_0.thru_0",
                f"child_{N_CHILDREN-1}.thru_0 -> out_0",
                *[f"child_{i}.thru_0 -> child_{i+1}.thru_0" for i in range(N_CHILDREN - 1)],
            ],
        },
    }

    assert verify_topology(qref_obj)
