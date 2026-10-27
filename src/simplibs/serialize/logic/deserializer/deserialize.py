from typing import Any, TypeVar, overload
from simplibs.validate import validate_call
# Outers
from ...annotations import TargetType
# Inners
from ._builders import build_value
from ._classes import DeserializeContext
from ._validations import raise_data_too_deep_error
# Annotations
T = TypeVar("T")


@overload
def deserialize(data: Any, annotation: type[T], *, strict: bool = True) -> T: ...
@overload
def deserialize(data: Any, annotation: TargetType, *, strict: bool = True) -> Any: ...


@validate_call
def deserialize(
    data: Any,
    annotation: TargetType,
    *,
    strict: bool = True,
) -> Any:
    """Build a value of the given type from ..d data.

    Args:
        data: The serialized data (from `serialize`, or any JSON-decoded structure).
        annotation: What to build: a class, a dataclass, `list[int]`,
            `dict[str, Point]`, `int | None`, `Literal["a", "b"]`, an enum, ...
        strict: If True, a dataclass, `NamedTuple` or `TypedDict` refuses data
            with keys it does not know. If False, those keys are ignored.

    Returns:
        A value of the requested type.

    Raises:
        DeserializationError: If the data does not fit the annotation, or the
            annotation is not supported. The card names the location of the
            value, for example `$.servers[2].port`.
        ParamError: For a dataclass field with invalid `metadata` options.

    Supported annotations: `str`, `int`, `float`, `bool`, `None`, `Any`; `list`,
    `set`, `frozenset`, `deque`, `tuple`, `dict`, `OrderedDict` and the abstract
    `Sequence` / `Set` / `Mapping` family, bare or subscripted; `X | Y`,
    `Optional`, `Annotated` (its rules are checked), `Literal`, `NewType`,
    `type` aliases; dataclasses (also generic ones), `NamedTuple`, `TypedDict`;
    every enum; and every type built in or registered with `register_type()`.

    Example:
        deserialize({"x": 1, "y": 2}, Point)
        deserialize(["2024-01-02"], list[date])
    """

    # 1. Everything one call needs is carried in one object
    context = DeserializeContext(strict=strict, build_value=build_value)

    # 2. Build from the root; data nested beyond the interpreter's limit gets a card
    try:
        return context.build(data, annotation, ())
    except RecursionError:
        raise_data_too_deep_error()


_DESIGN_NOTES = """
# deserialize — Data and an Annotation to a Value

## Purpose
The way back. The annotation is the schema: nothing is guessed from the data.

## Why the Annotation Is the Schema
With `Point | Circle` the data alone cannot say which is meant; with
`dict[str, int]` it cannot say the values are ints. The caller knows, so the
caller says.
"""
