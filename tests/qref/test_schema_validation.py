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

"""Test cases checking that schema matches data that we expect it to match."""

from pathlib import Path

import pydantic
import pytest
import yaml  # type: ignore[import-untyped]
from jsonschema import ValidationError, validate

from qref import SchemaV1, generate_program_schema


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


@pytest.mark.parametrize("input, error_path, error_message", load_invalid_examples())
def test_invalid_program_fails_to_validate_with_schema_v1(input, error_path, error_message):
    with pytest.raises(ValidationError) as err_info:
        validate_with_v1(input)

    assert err_info.value.json_path == error_path
    assert err_info.value.message == error_message


def test_valid_program_successfully_validates_with_schema_v1(valid_program):
    validate_with_v1(valid_program)


@pytest.mark.parametrize("input", [input for input, *_ in load_invalid_examples()])
def test_invalid_program_fails_to_validate_with_pydantic_model_v1(input):
    with pytest.raises(pydantic.ValidationError):
        SchemaV1.model_validate(input)


def test_valid_program_succesfully_validate_with_pydantic_model_v1(valid_program):
    SchemaV1.model_validate(valid_program)
