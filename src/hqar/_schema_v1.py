"""
..  Copyright © 2023-2024 PsiQuantum Corp.  All rights reserved.
    PSIQUANTUM CORP. CONFIDENTIAL
    This file includes unpublished proprietary source code of PsiQuantum Corp.
    The copyright notice above does not evidence any actual or intended publication
    of such source code. Disclosure of this source code or any related proprietary
    information is strictly prohibited without the express written permission of
    PsiQuantum Corp.

Pydantic models used for defining V1 schema of Routine.
"""
from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pydantic.json_schema import GenerateJsonSchema

NAME_PATTERN = "[A-Za-z_][A-Za-z0-9_]*"
NAMESPACED_NAME_PATTERN = rf"{NAME_PATTERN}\.{NAME_PATTERN}"


Name = Annotated[str, StringConstraints(pattern=rf"^{NAME_PATTERN}$")]
NamespacedName = Annotated[str, StringConstraints(pattern=rf"^{NAMESPACED_NAME_PATTERN}")]
OptionallyNamespacedName = Annotated[
    str, StringConstraints(pattern=rf"^(({NAME_PATTERN})|({NAMESPACED_NAME_PATTERN}))$")
]
_Value = Union[int, float, str]


class _PortV1(BaseModel):
    name: Name
    direction: Literal["input", "output", "through"]
    size: Optional[_Value]
    model_config = ConfigDict(title="Port")


class _ConnectionV1(BaseModel):
    source: OptionallyNamespacedName
    target: OptionallyNamespacedName

    model_config = ConfigDict(title="Connection", use_enum_values=True)


class _ResourceV1(BaseModel):
    name: Name
    type: Literal["additive", "multiplicative", "qubits", "other"]
    value: Union[int, float, str, None]

    model_config = ConfigDict(title="Resource")


class _ParamLinkV1(BaseModel):
    source: Name
    targets: list[NamespacedName]

    model_config = ConfigDict(title="ParamLink")


class RoutineV1(BaseModel):
    """Description of Routine in V1 schema.

    Note:
        This is NOT a top-level object in the schema. Instead, RoutineV1 is wrapped in
        SchemaV1.
    """

    name: Name
    children: list[RoutineV1] = Field(default_factory=list)
    type: Optional[str] = None
    ports: list[_PortV1] = Field(default_factory=list)
    resources: list[_ResourceV1] = Field(default_factory=list)
    connections: list[_ConnectionV1] = Field(default_factory=list)
    input_params: list[Name] = Field(default_factory=list)
    local_variables: list[str] = Field(default_factory=list)
    linked_params: list[_ParamLinkV1] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(title="Routine")

    def __init__(self, **data: Any):
        super().__init__(**{k: v for k, v in data.items() if v != [] and v != {}})


class SchemaV1(BaseModel):
    """Root object in Program schema V1."""

    version: Literal["v1"]
    program: RoutineV1


class _GenerateV1JsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        json_schema = super().generate(schema, mode=mode)
        json_schema["title"] = "FTQC-ready quantum program"
        json_schema["$schema"] = self.schema_dialect
        return json_schema

    def normalize_name(self, name):
        return name.removeprefix("_").replace("V1", "")


def generate_schema_v1() -> dict[str, Any]:
    """Generate Routine schema V1.

    The schema is generated from DocumentRootV1 model, and then enriched with
    additional fields "title" and "$schema".
    """
    return SchemaV1.model_json_schema(schema_generator=_GenerateV1JsonSchema)