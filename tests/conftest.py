"""Common fixtures for QART tests."""

from pathlib import Path

import pytest
import yaml

VALID_PROGRAMS_ROOT_PATH = Path(__file__).parent / "qart/data/valid_programs"


def _load_valid_examples():
    for path in VALID_PROGRAMS_ROOT_PATH.iterdir():
        with open(path) as f:
            data = yaml.safe_load(f)
            yield pytest.param(data["input"], id=data["description"])


@pytest.fixture(params=_load_valid_examples())
def valid_program(request):
    return request.param
