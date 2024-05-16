"""
..  Copyright © 2023-2024 PsiQuantum Corp.  All rights reserved.
    PSIQUANTUM CORP. CONFIDENTIAL
    This file includes unpublished proprietary source code of PsiQuantum Corp.
    The copyright notice above does not evidence any actual or intended publication
    of such source code. Disclosure of this source code or any related proprietary
    information is strictly prohibited without the express written permission of
    PsiQuantum Corp.

Test cases for Knifey-Qualtran integration.
"""

import pytest
from qualtran import Bloq, BloqBuilder
from qualtran.bloqs.basic_gates import CNOT
from qualtran.bloqs.arithmetic.comparison import LessThanEqual
from qualtran.bloqs.state_preparation import StatePreparationAliasSampling
from qualtran.bloqs.hamiltonian_simulation.hamiltonian_simulation_by_gqsp import (
    HamiltonianSimulationByGQSP,
)
from qualtran.bloqs.data_loading.qrom import QROM
from qualtran.bloqs.hubbard_model import get_walk_operator_for_hubbard_model
from ._schema_v1 import RoutineV1
from .qualtran_integration import import_from_qualtran
import sympy


def _cnot_routine(name: str) -> RoutineV1:
    return RoutineV1(
        name=name,
        type="CNOT",
        ports=[
            {"name": "in_ctrl", "size": 1, "direction": "input"},
            {"name": "in_target", "size": 1, "direction": "input"},
            {"name": "out_ctrl", "size": 1, "direction": "output"},
            {"name": "out_target", "size": 1, "direction": "output"},
        ],
        resources=[
            {"name": "clifford", "value": 1, "type": "additive"},
            {"name": "rotations", "value": 0, "type": "additive"},
            {"name": "t", "value": 0, "type": "additive"},
        ],
    )


def _two_connected_cnots_case() -> tuple[Bloq, RoutineV1, str]:
    # This example is taken from:
    # https://qualtran.readthedocs.io/en/latest/_infra/composite_bloq.html#bloq-builder
    # (first example in section)

    # Prepare Qualtran Bloq
    cnot = CNOT()
    bb = BloqBuilder()
    q0 = bb.add_register("q0", 1)
    q1 = bb.add_register("q1", 1)
    q0, q1 = bb.add(cnot, ctrl=q0, target=q1)
    q0, q1 = bb.add(cnot, ctrl=q0, target=q1)
    cbloq = bb.finalize(q0=q0, q1=q1)

    # Prepare qref Routine
    routine = RoutineV1(
        name="CompositeBloq",
        type="CompositeBloq",
        children=[_cnot_routine("CNOT_0"), _cnot_routine("CNOT_1")],
        ports=sorted(
            [
                {"name": "in_q0", "size": 1, "direction": "input"},
                {"name": "in_q1", "size": 1, "direction": "input"},
                {"name": "out_q0", "size": 1, "direction": "output"},
                {"name": "out_q1", "size": 1, "direction": "output"},
            ],
            key=lambda p: p["name"],
        ),
        connections=[
            {"source": "in_q0", "target": "CNOT_0.in_ctrl"},
            {"source": "in_q1", "target": "CNOT_0.in_target"},
            {"source": "CNOT_0.out_ctrl", "target": "CNOT_1.in_ctrl"},
            {"source": "CNOT_0.out_target", "target": "CNOT_1.in_target"},
            {"source": "CNOT_1.out_target", "target": "out_q1"},
            {"source": "CNOT_1.out_ctrl", "target": "out_q0"},
        ],
        resources=[
            {"name": "clifford", "value": 2, "type": "additive"},
            {"name": "rotations", "value": 0, "type": "additive"},
            {"name": "t", "value": 0, "type": "additive"},
        ],
    )

    return cbloq, routine, "two connected CNOTs"


def _two_cross_connected_cnots_case() -> tuple[Bloq, RoutineV1, str]:
    # This example is taken from:
    # https://qualtran.readthedocs.io/en/latest/_infra/composite_bloq.html#bloq-builder
    # (second example in section)

    # Prepare Qualtran Bloq
    cnot = CNOT()
    bb = BloqBuilder()
    q0 = bb.add_register("q0", 1)
    q1 = bb.add_register("q1", 1)
    q0, q1 = bb.add(cnot, ctrl=q0, target=q1)
    q0, q1 = bb.add(cnot, ctrl=q1, target=q0)
    cbloq = bb.finalize(q0=q0, q1=q1)

    # Prepare knifey RoutineV1
    routine = RoutineV1(
        name="CompositeBloq",
        type="CompositeBloq",
        children=[_cnot_routine("CNOT_0"), _cnot_routine("CNOT_1")],
        ports=[
            {"name": "in_q0", "size": 1, "direction": "input"},
            {"name": "in_q1", "size": 1, "direction": "input"},
            {"name": "out_q0", "size": 1, "direction": "output"},
            {"name": "out_q1", "size": 1, "direction": "output"},
        ],
        connections=[
            {"source": "in_q0", "target": "CNOT_0.in_ctrl"},
            {"source": "in_q1", "target": "CNOT_0.in_target"},
            {"source": "CNOT_0.out_ctrl", "target": "CNOT_1.in_target"},
            {"source": "CNOT_0.out_target", "target": "CNOT_1.in_ctrl"},
            {"source": "CNOT_1.out_target", "target": "out_q1"},
            {"source": "CNOT_1.out_ctrl", "target": "out_q0"},
        ],
        resources=[
            {"name": "clifford", "value": 2, "type": "additive"},
            {"name": "rotations", "value": 0, "type": "additive"},
            {"name": "t", "value": 0, "type": "additive"},
        ],
    )

    return cbloq, routine, "two cross connected CNOTs"


def _undecomposed_alias_sampling_test_case() -> tuple[Bloq, RoutineV1, str]:
    bloq = StatePreparationAliasSampling.from_lcu_probs([0.25, 0.5, 0.25], probability_epsilon=0.05)

    routine = RoutineV1(
        name="StatePreparationAliasSampling",
        type="StatePreparationAliasSampling",
        ports=[
            {"name": "in_selection", "size": 2, "direction": "input"},
            {"name": "in_sigma_mu", "size": 3, "direction": "input"},
            {"name": "in_alt", "size": 2, "direction": "input"},
            {"name": "in_keep", "size": 3, "direction": "input"},
            {
                "name": "in_less_than_equal",
                "size": 1,
                "direction": "input",
            },
            {
                "name": "out_selection",
                "size": 2,
                "direction": "output",
            },
            {"name": "out_sigma_mu", "size": 3, "direction": "output"},
            {"name": "out_alt", "size": 2, "direction": "output"},
            {"name": "out_keep", "size": 3, "direction": "output"},
            {
                "name": "out_less_than_equal",
                "size": 1,
                "direction": "output",
            },
        ],
        resources=[
            {"name": "clifford", "value": 272, "type": "additive"},
            {"name": "rotations", "value": 2, "type": "additive"},
            {"name": "t", "value": 58, "type": "additive"},
        ],
    )

    return bloq, routine, "alias sampling (undecomposed)"


def _decomposed_alias_sampling_test_case() -> tuple[Bloq, RoutineV1, str]:
    bloq = StatePreparationAliasSampling.from_lcu_probs(
        [0.25, 0.5, 0.25], probability_epsilon=0.05
    ).decompose_bloq()

    routine = RoutineV1(
        name="CompositeBloq",
        type="CompositeBloq",
        ports=[
            {"name": "in_selection", "size": 2, "direction": "input"},
            {"name": "in_sigma_mu", "size": 3, "direction": "input"},
            {"name": "in_alt", "size": 2, "direction": "input"},
            {"name": "in_keep", "size": 3, "direction": "input"},
            {
                "name": "in_less_than_equal",
                "size": 1,
                "direction": "input",
            },
            {
                "name": "out_selection",
                "size": 2,
                "direction": "output",
            },
            {"name": "out_sigma_mu", "size": 3, "direction": "output"},
            {"name": "out_alt", "size": 2, "direction": "output"},
            {"name": "out_keep", "size": 3, "direction": "output"},
            {
                "name": "out_less_than_equal",
                "size": 1,
                "direction": "output",
            },
        ],
        children=[
            RoutineV1(
                name="Split_1",
                type="Split",
                ports=[
                    {"name": "in_reg", "direction": "input", "size": 3},
                    {
                        "name": "out_reg_0",
                        "direction": "output",
                        "size": 1,
                    },
                    {
                        "name": "out_reg_1",
                        "direction": "output",
                        "size": 1,
                    },
                    {
                        "name": "out_reg_2",
                        "direction": "output",
                        "size": 1,
                    },
                ],
                resources=[
                    {"name": "clifford", "value": 0, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 0, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="Hadamard_2",
                type="Hadamard",
                ports=[
                    {"name": "in_q", "direction": "input", "size": 1},
                    {"name": "out_q", "direction": "output", "size": 1},
                ],
                resources=[
                    {"name": "clifford", "value": 1, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 0, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="Hadamard_3",
                type="Hadamard",
                ports=[
                    {"name": "in_q", "direction": "input", "size": 1},
                    {"name": "out_q", "direction": "output", "size": 1},
                ],
                resources=[
                    {"name": "clifford", "value": 1, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 0, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="Hadamard_4",
                type="Hadamard",
                ports=[
                    {"name": "in_q", "direction": "input", "size": 1},
                    {"name": "out_q", "direction": "output", "size": 1},
                ],
                resources=[
                    {"name": "clifford", "value": 1, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 0, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="CSwap_8",
                type="CSwap",
                ports=[
                    {"name": "in_ctrl", "direction": "input", "size": 1},
                    {"name": "out_ctrl", "direction": "output", "size": 1},
                    {"name": "in_x", "direction": "input", "size": 2},
                    {"name": "out_x", "direction": "output", "size": 2},
                    {"name": "in_y", "direction": "input", "size": 2},
                    {"name": "out_y", "direction": "output", "size": 2},
                ],
                resources=[
                    {"name": "clifford", "value": 20, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 14, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="Join_6",
                type="Join",
                ports=[
                    {"name": "out_reg", "direction": "output", "size": 3},
                    {"name": "in_reg_0", "direction": "input", "size": 1},
                    {"name": "in_reg_1", "direction": "input", "size": 1},
                    {"name": "in_reg_2", "direction": "input", "size": 1},
                ],
                resources=[
                    {"name": "clifford", "value": 0, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 0, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="LessThanEqual_7",
                type="LessThanEqual",
                ports=[
                    {"name": "in_x", "direction": "input", "size": 3},
                    {"name": "out_x", "direction": "output", "size": 3},
                    {"name": "in_y", "direction": "input", "size": 3},
                    {"name": "out_y", "direction": "output", "size": 3},
                    {"name": "in_target", "direction": "input", "size": 1},
                    {
                        "name": "out_target",
                        "direction": "output",
                        "size": 1,
                    },
                ],
                resources=[
                    {"name": "clifford", "value": 121, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 20, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="PrepareUniformSuperposition_0",
                type="PrepareUniformSuperposition",
                ports=[
                    {"name": "in_target", "direction": "input", "size": 2},
                    {
                        "name": "out_target",
                        "direction": "output",
                        "size": 2,
                    },
                ],
                resources=[
                    {"name": "clifford", "value": 103, "type": "additive"},
                    {"name": "rotations", "value": 2, "type": "additive"},
                    {"name": "t", "value": 20, "type": "additive"},
                ],
            ),
            RoutineV1(
                name="QROM_5",
                type="QROM",
                ports=[
                    {
                        "name": "in_selection",
                        "direction": "input",
                        "size": 2,
                    },
                    {
                        "name": "out_selection",
                        "direction": "output",
                        "size": 2,
                    },
                    {
                        "name": "in_target0_",
                        "direction": "input",
                        "size": 2,
                    },
                    {
                        "name": "out_target0_",
                        "direction": "output",
                        "size": 2,
                    },
                    {
                        "name": "in_target1_",
                        "direction": "input",
                        "size": 3,
                    },
                    {
                        "name": "out_target1_",
                        "direction": "output",
                        "size": 3,
                    },
                ],
                resources=[
                    {"name": "clifford", "value": 25, "type": "additive"},
                    {"name": "rotations", "value": 0, "type": "additive"},
                    {"name": "t", "value": 4, "type": "additive"},
                ],
            ),
        ],
        connections=[
            {"source": in_, "target": out_}
            for in_, out_ in [
                ("CSwap_8.out_ctrl", "out_less_than_equal"),
                ("CSwap_8.out_x", "out_alt"),
                ("CSwap_8.out_y", "out_selection"),
                ("Hadamard_2.out_q", "Join_6.in_reg_0"),
                ("Hadamard_3.out_q", "Join_6.in_reg_1"),
                ("Hadamard_4.out_q", "Join_6.in_reg_2"),
                ("Join_6.out_reg", "LessThanEqual_7.in_y"),
                ("LessThanEqual_7.out_target", "CSwap_8.in_ctrl"),
                ("LessThanEqual_7.out_x", "out_keep"),
                ("LessThanEqual_7.out_y", "out_sigma_mu"),
                ("PrepareUniformSuperposition_0.out_target", "QROM_5.in_selection"),
                ("QROM_5.out_selection", "CSwap_8.in_y"),
                ("QROM_5.out_target0_", "CSwap_8.in_x"),
                ("QROM_5.out_target1_", "LessThanEqual_7.in_x"),
                ("Split_1.out_reg_0", "Hadamard_2.in_q"),
                ("Split_1.out_reg_1", "Hadamard_3.in_q"),
                ("Split_1.out_reg_2", "Hadamard_4.in_q"),
                ("in_alt", "QROM_5.in_target0_"),
                ("in_keep", "QROM_5.in_target1_"),
                ("in_less_than_equal", "LessThanEqual_7.in_target"),
                ("in_selection", "PrepareUniformSuperposition_0.in_target"),
                ("in_sigma_mu", "Split_1.in_reg"),
            ]
        ],
        resources=[
            {"name": "clifford", "value": 272, "type": "additive"},
            {"name": "rotations", "value": 2, "type": "additive"},
            {"name": "t", "value": 58, "type": "additive"},
        ],
    )

    return bloq, routine, "alias sampling (decomposed)"


def _less_than_equal_test_case() -> tuple[Bloq, RoutineV1, str]:
    bloq = LessThanEqual(10, 15)
    routine = RoutineV1(
        name="LessThanEqual",
        type="LessThanEqual",
        ports=[
            {"name": "in_target", "direction": "input", "size": 1},
            {"name": "in_x", "direction": "input", "size": 10},
            {"name": "in_y", "direction": "input", "size": 15},
            {"name": "out_target", "direction": "output", "size": 1},
            {"name": "out_x", "direction": "output", "size": 10},
            {"name": "out_y", "direction": "output", "size": 15},
        ],
        resources=[
            {"name": "clifford", "type": "additive", "value": 533},
            {"name": "rotations", "type": "additive", "value": 0},
            {"name": "t", "type": "additive", "value": 96},
        ],
    )

    return bloq, routine, "less than equal"


def _less_than_equal_symbolic_test_case() -> tuple[Bloq, RoutineV1, str]:
    a, b = sympy.symbols("a b")
    bloq = LessThanEqual(a, b)
    routine = RoutineV1(
        name="LessThanEqual",
        type="LessThanEqual",
        ports=[
            {"name": "in_target", "direction": "input", "size": 1},
            {"name": "in_x", "direction": "input", "size": 10},
            {"name": "in_y", "direction": "input", "size": 15},
            {"name": "out_target", "direction": "output", "size": 1},
            {"name": "out_x", "direction": "output", "size": 10},
            {"name": "out_y", "direction": "output", "size": 15},
        ],
        resources=[
            {"name": "clifford", "type": "additive", "value": 533},
            {"name": "rotations", "type": "additive", "value": 0},
            {"name": "t", "type": "additive", "value": 96},
        ],
    )
    return bloq, routine, "less than equal"


def _qrom_symbolic_test_case() -> tuple[Bloq, RoutineV1, str]:
    N, M, b1, b2, c = sympy.symbols("N M b1 b2 c")
    bloq = QROM.build_from_bitsize((N, M), (b1, b2), num_controls=c)
    routine = RoutineV1(
        name="LessThanEqual",
        type="LessThanEqual",
        ports=[
            {"name": "in_target", "direction": "input", "size": 1},
            {"name": "in_x", "direction": "input", "size": 10},
            {"name": "in_y", "direction": "input", "size": 15},
            {"name": "out_target", "direction": "output", "size": 1},
            {"name": "out_x", "direction": "output", "size": 10},
            {"name": "out_y", "direction": "output", "size": 15},
        ],
        resources=[
            {"name": "clifford", "type": "additive", "value": 533},
            {"name": "rotations", "type": "additive", "value": 0},
            {"name": "t", "type": "additive", "value": 96},
        ],
    )
    breakpoint()
    return bloq, routine, "less than equal"


def _hamiltonian_simulation_test_case() -> tuple[Bloq, RoutineV1, str]:
    walk_op = get_walk_operator_for_hubbard_model(2, 2, 1, 1)
    t, inv_eps = sympy.symbols("t N")
    symbolic_hamsim_by_gqsp = HamiltonianSimulationByGQSP(walk_op, t=t, precision=1 / inv_eps)

    walk_op = get_walk_operator_for_hubbard_model(2, 2, 1, 1)
    hubbard_time_evolution_by_gqsp = HamiltonianSimulationByGQSP(walk_op, t=5, precision=1e-7)
    hubbard_time_evolution_by_gqsp.t_complexity()
    breakpoint()


@pytest.mark.parametrize(
    "qualtran_object, expected_routine",
    [
        pytest.param(operation, bloq, id=case_id)
        for operation, bloq, case_id in [
            _two_connected_cnots_case(),
            _two_cross_connected_cnots_case(),
            _less_than_equal_test_case(),
            # _less_than_equal_symbolic_test_case(),
            _qrom_symbolic_test_case(),
            _undecomposed_alias_sampling_test_case(),
            _decomposed_alias_sampling_test_case(),
            # _hamiltonian_simulation_test_case(),
        ]
    ],
)
def test_importing_qualtran_object_gives_expected_routine_object(qualtran_object, expected_routine):
    assert expected_routine == import_from_qualtran(qualtran_object)
