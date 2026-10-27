from typing import Any, NoReturn
# Outers
from ....exceptions import SerializationError
from ..._common_helpers import format_location, Location


def raise_unsupported_type_error(
    location: Location,

    obj: Any) -> NoReturn:
    """Raise SerializationError when nothing knows how to convert the value.

    Args:
        location: Where in the data the value sits.
        obj: The value that cannot be converted.
    """

    # 1. Raise structured SerializationError wrapping a TypeError
    type_name = type(obj).__name__
    raise SerializationError(
        error_name="SERIALIZE_UNSUPPORTED_TYPE",
        label=format_location(location),
        value=obj,
        problem=f"No serializer is known for type '{type_name}'.",
        expected=(
            "A primitive, a list / tuple / set / mapping, a dataclass instance, "
            "a NamedTuple, an enum member, or a type that is built in or "
            "registered with register_type()."
        ),
        how_to_fix=(
            f"Register a handler: register_type({type_name}, to_func=...).",
            "Or pass `default=` to serialize() to deal with such objects in one place.",
            "Or convert the value yourself before serializing it.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_unsupported_type_error — Nobody Knows This Type

## Purpose
With a thousand values in a structure, "type 'Point'" without a location is a
search. The label is the location of the value.

## Three Ways Out
Each one fits a different situation: a type that is used often (register it),
a mixed bag of leftovers (`default=`), a one-off (convert it).
"""
