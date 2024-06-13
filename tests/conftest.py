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

from pathlib import Path

import pytest
import yaml

VALID_PROGRAMS_ROOT_PATH = Path(__file__).parent / "qref/data/valid_programs"


def _load_valid_examples():
    for path in sorted(VALID_PROGRAMS_ROOT_PATH.iterdir()):
        with open(path) as f:
            data = yaml.safe_load(f)
            yield pytest.param(data["input"], id=data["description"])


@pytest.fixture(params=_load_valid_examples())
def valid_program(request):
    return request.param
