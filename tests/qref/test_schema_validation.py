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
import pydantic
import pytest
from jsonschema import ValidationError, validate

from qref import SchemaV1, generate_program_schema


def validate_with_v1(data):
    validate(data, generate_program_schema(version="v1"))


@pytest.mark.invalid_schema_examples
def test_invalid_program_fails_to_validate_with_schema_v1(input, error_path, error_message):
    with pytest.raises(ValidationError) as err_info:
        validate_with_v1(input)

    assert err_info.value.json_path == error_path
    assert err_info.value.message == error_message


def test_valid_program_successfully_validates_with_schema_v1(valid_program):
    validate_with_v1(valid_program)


@pytest.mark.invalid_pydantic_examples
def test_invalid_program_fails_to_validate_with_pydantic_model_v1(input):
    with pytest.raises(pydantic.ValidationError) as e:
        SchemaV1.model_validate(input)
    print(e.value)


def test_valid_program_succesfully_validate_with_pydantic_model_v1(valid_program):
    SchemaV1.model_validate(valid_program)
