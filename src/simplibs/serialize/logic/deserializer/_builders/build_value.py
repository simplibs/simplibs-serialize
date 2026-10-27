import dataclasses
from types import NoneType
from typing import Any, get_origin, is_typeddict
# Outers
from ..._common_helpers import is_named_tuple_class, Location
from ..._constants import JSON_PRIMITIVES
from ...registry import find_from_handler
from .._classes import DeserializeContext
from .._helpers import is_alias_annotation
from .._validations import raise_unsupported_annotation_error, raise_wrong_type_error
# Inners
from .BUILDER_TABLE import BUILDER_TABLE
from .build_alias_value import build_alias_value
from .build_dataclass_value import build_dataclass_value
from .build_named_tuple_value import build_named_tuple_value
from .build_primitive_value import build_primitive_value
from .build_typed_dict_value import build_typed_dict_value
from .build_with_handler import build_with_handler


def build_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build one value of the given annotation from the given data.

    Args:
        data: The serialized data at this location.
        annotation: What the data should become.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The built value.
    """

    # 1. Anything goes
    if annotation is Any or annotation is object:
        return data

    # 2. A registered or built-in handler — enums, dates, paths, UUIDs, your types.
    #    A class never receives None: that would be a TypeError inside the handler
    handler = find_from_handler(annotation)
    if handler is not None:
        if data is None and isinstance(annotation, type) and get_origin(annotation) is None:
            raise_wrong_type_error(location, annotation, data)
        return build_with_handler(handler, data, annotation, location)

    # 3. None
    if annotation is None or annotation is NoneType:
        if data is not None:
            raise_wrong_type_error(location, annotation, data)
        return None

    # 4. str, int, float, bool and their subclasses
    if (
        isinstance(annotation, type)
        and get_origin(annotation) is None
        and issubclass(annotation, JSON_PRIMITIVES)
    ):
        return build_primitive_value(data, annotation, location)

    # 5. Containers, unions, Annotated, Literal... — by the origin of the annotation
    origin = get_origin(annotation)
    try:
        builder = BUILDER_TABLE.get(annotation if origin is None else origin)
    except TypeError:
        builder = None
    if builder is not None:
        return builder(data, annotation, location, context)

    # 6. NewType, a `type` alias, a TypeVar — build what they stand for
    if is_alias_annotation(annotation):
        return build_alias_value(data, annotation, location, context)

    # 7. Classes with a structure of their own
    cls = annotation if origin is None else origin
    if isinstance(cls, type):
        if dataclasses.is_dataclass(cls):
            return build_dataclass_value(data, annotation, location, context)
        if is_typeddict(cls):
            return build_typed_dict_value(data, annotation, location, context)
        if is_named_tuple_class(cls):
            return build_named_tuple_value(data, annotation, location, context)

    # 8. Nothing recognized
    raise_unsupported_annotation_error(location, annotation)


_DESIGN_NOTES = """
# build_value — What Is Being Asked For

## Purpose
The one place where the order of decisions is written down.

## Why This Order
* A handler comes first, so whatever a user registers for a class, a `NewType` or
  an exact annotation such as `list[int]` wins over the general rule.
* `None` is decided by the annotation, never by the data: it is accepted for
  `None`, `Any`, `Optional` / unions that contain it — and for nothing else.
* Primitives before the table: `int` must not become a "container".
* The table before the classes: `list[Point]` is a list first.

## Enums
An enum class is found in step 2 through the `Enum` handler, found along the
class hierarchy; no enum-specific branch is needed.
"""
