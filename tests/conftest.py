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

"""Common fixtures for QREF tests."""
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

DATA_ROOT_PATH = Path(__file__).parent / "qref/data"
VALID_PROGRAMS_ROOT_PATH = DATA_ROOT_PATH / "valid_programs"
INVALID_YAML_PROGRAMS_PATH = DATA_ROOT_PATH / "invalid_yaml_programs.yaml"
INVALID_PYDANTIC_PROGRAMS_PATH = DATA_ROOT_PATH / "invalid_pydantic_programs.yaml"


def _load_valid_examples():
    for path in sorted(VALID_PROGRAMS_ROOT_PATH.iterdir()):
        with open(path) as f:
            data = yaml.safe_load(f)
            yield pytest.param(data["input"], id=data["description"])


@pytest.fixture(params=_load_valid_examples())
def valid_program(request):
    return request.param


@lru_cache(maxsize=None)
def _load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def pytest_generate_tests(metafunc):
    marker_names = [marker.name for marker in metafunc.definition.iter_markers()]
    if "invalid_schema_examples" in marker_names:
        data = _load_yaml(INVALID_YAML_PROGRAMS_PATH)
        metafunc.parametrize(
            "input, error_path, error_message",
            [
                pytest.param(
                    example["input"],
                    example["error_path"],
                    example["error_message"],
                    id=example["description"],
                )
                for example in data
            ],
        )
    elif "invalid_pydantic_examples" in marker_names:
        data = [
            example["input"]
            for example in (_load_yaml(INVALID_YAML_PROGRAMS_PATH) + _load_yaml(INVALID_PYDANTIC_PROGRAMS_PATH))
        ]
        metafunc.parametrize("input", data)
