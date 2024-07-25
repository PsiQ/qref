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

from typing import (
    Annotated,
    Any,
    Iterator,
    Literal,
    MutableMapping,
    Optional,
    TypeVar,
    Union,
    get_args,
)

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import core_schema
from typing_extensions import Self

NAME_PATTERN = "[A-Za-z_][A-Za-z0-9_]*"
OPTIONALLY_NAMESPACED_NAME_PATTERN = rf"({NAME_PATTERN}\.)?{NAME_PATTERN}"
MULTINAMESPACED_NAME_PATTERN = rf"({NAME_PATTERN}\.)+{NAME_PATTERN}"
OPTIONALLY_MULTINAMESPACED_NAME_PATTERN = rf"({NAME_PATTERN}\.)*{NAME_PATTERN}"
CONNECTION_PATTERN = rf"{OPTIONALLY_MULTINAMESPACED_NAME_PATTERN} -> {OPTIONALLY_MULTINAMESPACED_NAME_PATTERN}"

_Name = Annotated[str, StringConstraints(pattern=rf"^{NAME_PATTERN}$")]
_OptionallyNamespacedName = Annotated[str, StringConstraints(pattern=rf"^{OPTIONALLY_NAMESPACED_NAME_PATTERN}$")]
_MultiNamespacedName = Annotated[str, StringConstraints(pattern=rf"^{MULTINAMESPACED_NAME_PATTERN}$")]
_OptionallyMultiNamespacedName = Annotated[
    str, StringConstraints(pattern=rf"^{OPTIONALLY_MULTINAMESPACED_NAME_PATTERN}$")
]
_Value = Union[int, float, str]

T = TypeVar("T")


class _ProxyMapping(MutableMapping[str, T]):
    def __init__(self, source: list[T]):
        self.source = source

    def _find_item(self, name: str) -> tuple[int, T]:
        try:
            # To avoid the type: ignore below, we would have to define a protocol for named things,
            # which seems to be an overkill, especially that this class is private.
            return next(iter([(i, item) for i, item in enumerate(self.source) if item.name == name]))  # type: ignore
        except StopIteration:
            raise KeyError(name)

    def __getitem__(self, name: str) -> T:
        _index, item = self._find_item(name)
        return item

    def __setitem__(self, name: str, new_item: T) -> None:
        index, _current_item = self._find_item(name)
        self.source[index] = new_item

    def __delitem__(self, name: str):
        index, _current_item = self._find_item(name)
        del self.source[index]

    def __iter__(self) -> Iterator[str]:
        # Same reason for type: ignore as above
        return iter((item.name for item in self.source))  # type: ignore

    def __len__(self) -> int:
        return len(self.source)


class NamedList(list[T]):
    @property
    def by_name(self) -> _ProxyMapping[T]:
        return _ProxyMapping(self)

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        args = get_args(source)
        schema = handler.generate_schema(list[args[0]])
        return core_schema.no_info_after_validator_function(NamedList, schema)


def _sorter(key, cls=list):
    def _inner(v):
        return cls(sorted(v, key=key))

    return _inner


_name_sorter = AfterValidator(_sorter(lambda p: p.name, NamedList))
_source_sorter = AfterValidator(_sorter(lambda c: c.source))


def _parse_connection(connection):
    if isinstance(connection, str):
        source, target = connection.replace(" ", "").split("->")
        return {"source": source, "target": target}
    return connection


_connection_parser = BeforeValidator(_parse_connection)


CONNECTION_SCHEMA = {
    "type": "array",
    "items": {
        "anyOf": [
            {"$ref": "#/$defs/Connection"},
            {
                "pattern": f"^{CONNECTION_PATTERN}$",
                "type": "string",
            },
        ]
    },
    "title": "Connections",
    "type": "array",
}


class PortV1(BaseModel):
    """Description of Port in V1 schema"""

    name: _Name
    direction: Literal["input", "output", "through"]
    size: Optional[_Value]
    model_config = ConfigDict(title="Port")


class ConnectionV1(BaseModel):
    """Description of Connection in V1 schema"""

    source: _OptionallyNamespacedName
    target: _OptionallyNamespacedName

    model_config = ConfigDict(title="Connection", use_enum_values=True)


class ResourceV1(BaseModel):
    """Description of Resource in V1 schema"""

    name: _Name
    type: Literal["additive", "multiplicative", "qubits", "other"]
    value: Union[int, float, str, None]

    model_config = ConfigDict(title="Resource")


class ParamLinkV1(BaseModel):
    """Description of Parameter link in V1 schema"""

    source: _OptionallyNamespacedName
    targets: list[_MultiNamespacedName]

    model_config = ConfigDict(title="ParamLink")


class RoutineV1(BaseModel):
    """Description of Routine in V1 schema.

    Note:
        This is NOT a top-level object in the schema. Instead, RoutineV1 is wrapped in
        SchemaV1.
    """

    name: _Name
    children: Annotated[NamedList[RoutineV1], _name_sorter] = Field(default_factory=list)
    type: Optional[str] = None
    ports: Annotated[NamedList[PortV1], _name_sorter] = Field(default_factory=list)
    resources: Annotated[NamedList[ResourceV1], _name_sorter] = Field(default_factory=list)
    connections: Annotated[list[Annotated[ConnectionV1, _connection_parser]], _source_sorter] = Field(
        default_factory=list
    )
    input_params: list[_OptionallyMultiNamespacedName] = Field(default_factory=list)
    local_variables: dict[str, str] = Field(default_factory=dict)
    linked_params: Annotated[list[ParamLinkV1], _source_sorter] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(title="Routine", validate_assignment=True)

    def __init__(self, **data: Any):
        super().__init__(**{k: v for k, v in data.items() if v != [] and v != {}})

    @model_validator(mode="after")
    def _validate_connections(self) -> Self:
        children_port_names = [f"{child.name}.{port.name}" for child in self.children for port in child.ports]
        parent_port_names = [port.name for port in self.ports]
        available_port_names = set(children_port_names + parent_port_names)

        missed_ports = [
            port
            for connection in self.connections
            for port in (connection.source, connection.target)
            if port not in available_port_names
        ]
        if missed_ports:
            raise ValueError(
                "The following ports appear in a connection but are not "
                "among routine's port or their children's ports: {missed_ports}."
            )
        return self


class SchemaV1(BaseModel):
    """Root object in Program schema V1."""

    version: Literal["v1"]
    program: RoutineV1


class _GenerateV1JsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        json_schema = super().generate(schema, mode=mode)
        json_schema["title"] = "FTQC-ready quantum program"
        json_schema["$schema"] = self.schema_dialect
        json_schema["$defs"]["Routine"]["properties"]["connections"] = CONNECTION_SCHEMA
        return json_schema

    def normalize_name(self, name):
        return name.removeprefix("_").replace("V1", "")


def generate_schema_v1() -> dict[str, Any]:
    """Generate Routine schema V1.

    The schema is generated from DocumentRootV1 model, and then enriched with
    additional fields "title" and "$schema".
    """
    return SchemaV1.model_json_schema(schema_generator=_GenerateV1JsonSchema)
