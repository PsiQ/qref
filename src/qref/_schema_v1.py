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

"""Pydantic models used for defining V1 schema of Routine."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints
from pydantic.json_schema import GenerateJsonSchema

NAME_PATTERN = "[A-Za-z_][A-Za-z0-9_]*"
NAMESPACED_NAME_PATTERN = rf"{NAME_PATTERN}\.{NAME_PATTERN}"

Name = Annotated[str, StringConstraints(pattern=rf"^{NAME_PATTERN}$")]
NamespacedName = Annotated[str, StringConstraints(pattern=rf"^{NAMESPACED_NAME_PATTERN}")]
OptionallyNamespacedName = Annotated[
    str, StringConstraints(pattern=rf"^(({NAME_PATTERN})|({NAMESPACED_NAME_PATTERN}))$")
]
_Value = Union[int, float, str]


def sorter(key):
    def _inner(v):
        return sorted(v, key=key)

    return _inner


name_sorter = AfterValidator(sorter(lambda p: p.name))
source_sorter = AfterValidator(sorter(lambda c: c.source))


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
    children: Annotated[list[RoutineV1], name_sorter] = Field(default_factory=list)
    type: Optional[str] = None
    ports: Annotated[list[_PortV1], name_sorter] = Field(default_factory=list)
    resources: Annotated[list[_ResourceV1], name_sorter] = Field(default_factory=list)
    connections: Annotated[list[_ConnectionV1], source_sorter] = Field(default_factory=list)
    input_params: list[Name] = Field(default_factory=list)
    local_variables: list[str] = Field(default_factory=list)
    linked_params: Annotated[list[_ParamLinkV1], source_sorter] = Field(default_factory=list)
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
