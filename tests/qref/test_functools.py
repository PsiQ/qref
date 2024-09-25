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
