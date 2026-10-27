import json
from typing import Any, TypeVar, overload
from simplibs.validate import validate_call
# Outers
from ...annotations import TargetType
from ..deserializer import deserialize
# Inners
from ._validations import raise_invalid_json_error
# Annotations
T = TypeVar("T")


@overload
def from_json(json_str: str | bytes, annotation: type[T], *, strict: bool = True) -> T: ...
@overload
def from_json(json_str: str | bytes, annotation: TargetType, *, strict: bool = True) -> Any: ...


@validate_call
def from_json(
    json_str: str | bytes,
    annotation: TargetType,
    *,
    strict: bool = True,
) -> Any:
    """Read JSON text and build a value of the given type from it.

    Args:
        json_str: The JSON text (or UTF-8 bytes).
        annotation: What to build: a class, `list[Point]`, `dict[str, int]`, ...
        strict: As for `deserialize`: unknown keys are an error.

    Returns:
        A value of the requested type.

    Raises:
        DeserializationError: If the text is not valid JSON (with line and
            column), or the JSON does not fit the annotation.
    """

    # 1. A BOM in front of text is not part of the JSON (bytes are handled by `json.loads`)
    if isinstance(json_str, str):
        json_str = json_str.removeprefix("\ufeff")
    # 2. Parse; a syntax error becomes a card with a position and an excerpt
    try:
        data = json.loads(json_str)
    except (ValueError, RecursionError) as caught:
        raise_invalid_json_error(json_str, caught)

    # 3. Build the value
    return deserialize(data, annotation, strict=strict)


_DESIGN_NOTES = """
# from_json — JSON Text to Object
## `NaN` Is Read
`json.loads` accepts `NaN` and `Infinity`, and so does this function — the same
leniency as `read_json`. A float field takes them; an `Annotated` rule decides
whether that is acceptable.

## BOM and Depth
A BOM at the start of a `str` is not part of the JSON and is dropped (bytes are
handled by `json.loads` itself). Text nested beyond the interpreter's limit raises a
`RecursionError` inside `json.loads`; it becomes the same invalid-JSON card.
"""
