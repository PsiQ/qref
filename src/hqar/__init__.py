"""
..  Copyright © 2023-2024 PsiQuantum Corp.  All rights reserved.
    PSIQUANTUM CORP. CONFIDENTIAL
    This file includes unpublished proprietary source code of PsiQuantum Corp.
    The copyright notice above does not evidence any actual or intended publication
    of such source code. Disclosure of this source code or any related proprietary
    information is strictly prohibited without the express written permission of
    PsiQuantum Corp.

Public API of HQAR.
"""
from typing import Any

from ._schema_v1 import generate_schema_v1

SCHEMA_GENERATORS = {"v1": generate_schema_v1}
LATEST_SCHEMA_VERSION = "v1"


def generate_program_schema(version: str = LATEST_SCHEMA_VERSION) -> dict[str, Any]:
    """Generate Program schema of given version.

    Args:
        version: version identifier of the schema.

    Returns:
        A dictionary with JSON schema describing program.

    Raises:
        ValueError: if `version` does not match any known version schema.
    """
    try:
        return SCHEMA_GENERATORS[version]()
    except KeyError:
        raise ValueError(f"Unknown schema version {version}")


__all__ = ["generate_program_schema"]
