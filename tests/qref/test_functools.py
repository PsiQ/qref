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
from qref.functools import accepts_all_qref_types, ensure_routine
from qref.schema_v1 import RoutineV1, SchemaV1


def test_ensure_routine_produces_correct_routine_v1_object(valid_program):
    outputs = [
        ensure_routine(valid_program),
        ensure_routine(valid_program["program"]),
        ensure_routine(SchemaV1(**valid_program)),
        ensure_routine(RoutineV1(**valid_program["program"])),
    ]

    assert outputs[0] == outputs[1] == outputs[2] == outputs[3]


def test_callables_can_be_augmented_to_accept_all_qref_types(valid_program):

    @accepts_all_qref_types
    def identity(r: RoutineV1) -> RoutineV1:
        return r

    outputs = [
        identity(valid_program),
        identity(valid_program["program"]),
        identity(SchemaV1(**valid_program)),
        identity(RoutineV1(**valid_program["program"])),
    ]

    assert all(isinstance(output, RoutineV1) for output in outputs)

    assert outputs[0] == outputs[1] == outputs[2] == outputs[3]
