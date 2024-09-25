from functools import singledispatch, wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

from .schema_v1 import RoutineV1, SchemaV1


@singledispatch
def ensure_routine(data: dict[str, Any]) -> RoutineV1:
    """Ensure that given objects is of RoutineV1 type.

    This functions may serve for constructing functions accepting either RoutineV1 oor SchemaV1
    objects, as well as dictionaries that represent them.

    Args:
        data: the objects that has to be converted (if neccessary) to RoutineV1. Can either be
        an instance of SchemaV1, in which case its `program` attribute will be returned,
        an instance of RoutineV1, in which case the object will be returned without changes,
        or a dictionary, in which case it will serve to constructe RoutineV1, or SchemaV1.

    Returns:
        Ann object of type RoutineV1 corresponding to the provided data.
    """
    return SchemaV1(**data).program if "version" in data else RoutineV1(**data)


@ensure_routine.register
def _ensure_routine_from_schema_v1(data: SchemaV1) -> RoutineV1:
    return data.program


@ensure_routine.register
def _ensure_routine_from_routine_v1(data: RoutineV1) -> RoutineV1:
    return data


P = ParamSpec("P")
T = TypeVar("T")


def accepts_all_qref_types(
    f: Callable[Concatenate[RoutineV1, P], T]
) -> Callable[Concatenate[SchemaV1 | RoutineV1 | dict[str, Any], P], T]:
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
