"""
..  Copyright © 2023-2024 PsiQuantum Corp.  All rights reserved.
    PSIQUANTUM CORP. CONFIDENTIAL
    This file includes unpublished proprietary source code of PsiQuantum Corp.
    The copyright notice above does not evidence any actual or intended publication
    of such source code. Disclosure of this source code or any related proprietary
    information is strictly prohibited without the express written permission of
    PsiQuantum Corp.

Test cases checking that schema matches data that we expect it to match.
"""
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]
from jsonschema import ValidationError, validate

from hqar import generate_program_schema


def validate_with_v1(data):
    validate(data, generate_program_schema(version="v1"))


def load_invalid_examples():
    with open(Path(__file__).parent / "data/invalid_program_examples.yaml") as f:
        data = yaml.safe_load(f)

    return [
        pytest.param(
            example["input"],
            example["error_path"],
            example["error_message"],
            id=example["description"],
        )
        for example in data
    ]


def load_valid_examples():
    with open(Path(__file__).parent / "data/valid_program_examples.yaml") as f:
        data = yaml.safe_load(f)

    return [pytest.param(example["input"], id=example["description"]) for example in data]


@pytest.mark.parametrize("input, error_path, error_message", load_invalid_examples())
def test_invalid_schema_fail_to_validate(input, error_path, error_message):
    with pytest.raises(ValidationError) as err_info:
        validate_with_v1(input)

    assert err_info.value.json_path == error_path
    assert err_info.value.message == error_message


@pytest.mark.parametrize("input", load_valid_examples())
def test_valid_schema_fail_to_validate(input):
    validate_with_v1(input)
