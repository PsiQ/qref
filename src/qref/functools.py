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

"""Tools for constructing functions operating on Qref objects."""
from functools import singledispatch, wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

from .schema_v1 import RoutineV1, SchemaV1

AnyQrefType = dict[str, Any] | SchemaV1 | RoutineV1


@singledispatch
def ensure_routine(data: AnyQrefType) -> RoutineV1:
    """Ensure that given objects is of RoutineV1 type.

    This functions may serve for constructing functions accepting either RoutineV1 oor SchemaV1
    objects, as well as dictionaries that represent them.

    Args:
        data: the objects that has to be converted (if neccessary) to RoutineV1. Can either be
        an instance of SchemaV1, in which case its `program` attribute will be returned,
        an instance of RoutineV1, in which case the object will be returned without changes,
        or a dictionary, in which case it will serve to constructe RoutineV1, or SchemaV1.

    Returns:
        An object of type RoutineV1 corresponding to the provided data.
    """
    raise NotImplementedError()


@ensure_routine.register(dict)
def _ensure_routine_from_dict(data: dict[str, Any]) -> RoutineV1:
    return SchemaV1(**data).program if "version" in data else RoutineV1(**data)


@ensure_routine.register
def _ensure_routine_from_schema_v1(data: SchemaV1) -> RoutineV1:
    return data.program


@ensure_routine.register
def _ensure_routine_from_routine_v1(data: RoutineV1) -> RoutineV1:
    return data


P = ParamSpec("P")
T = TypeVar("T")


def accepts_all_qref_types(f: Callable[Concatenate[RoutineV1, P], T]) -> Callable[Concatenate[AnyQrefType, P], T]:
    """Make a callable accepting RoutineV1 as first arg capable of accepting arbitrary QREF object.

    Here, by arbitrary QREF object we mean either an instance of SchemaV1, an instance of RoutineV1,
    or any dictionary that can be converted to an instance of SchemaV1 or RoutineV1.

    Args:
        f: Callable to be augmented.

    Returns:
        A new callable preserving behavoiur of f, but also capable of accepting SchemaV1 instance or dicts
        as first arguments.
    """

    @wraps(f)
    def _inner(routine: SchemaV1 | RoutineV1 | dict[str, Any], *args: P.args, **kwargs: P.kwargs) -> T:
        return f(ensure_routine(routine), *args, **kwargs)

    return _inner
