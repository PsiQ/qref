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

"""Public API of QREF."""

from typing import Any

from .schema_v1 import SchemaV1, generate_schema_v1
from .verification import verify_topology

SCHEMA_GENERATORS = {"v1": generate_schema_v1}
MODELS = {"v1": SchemaV1}
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


__all__ = ["generate_program_schema", "SchemaV1", "verify_topology"]
