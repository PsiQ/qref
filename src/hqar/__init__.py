"""Public API of HQAR."""

from typing import Any

from ._schema_v1 import SchemaV1, generate_schema_v1

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


__all__ = ["generate_program_schema", "SchemaV1"]
