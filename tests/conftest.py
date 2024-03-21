"""
..  Copyright © 2023-2024 PsiQuantum Corp.  All rights reserved.
    PSIQUANTUM CORP. CONFIDENTIAL
    This file includes unpublished proprietary source code of PsiQuantum Corp.
    The copyright notice above does not evidence any actual or intended publication
    of such source code. Disclosure of this source code or any related proprietary
    information is strictly prohibited without the express written permission of
    PsiQuantum Corp.
"""
from pathlib import Path

import pytest
import yaml

VALID_PROGRAMS_ROOT_PATH = Path(__file__).parent / "hqar/data/valid_programs"


def _load_valid_examples():
    for path in VALID_PROGRAMS_ROOT_PATH.iterdir():
        with open(path) as f:
            data = yaml.safe_load(f)
            yield pytest.param(data["input"], id=data["description"])


@pytest.fixture(params=_load_valid_examples())
def valid_program(request):
    return request.param
