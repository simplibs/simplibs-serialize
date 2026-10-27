from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import format_location, Location


def raise_unsupported_annotation_error(
    location: Location,
    annotation: Any
) -> NoReturn:
    """Raise DeserializationError when nothing can build the annotation.

    Args:
        location: Where in the data the value sits.
        annotation: The annotation nothing handles.
    """

    # 1. Raise structured DeserializationError wrapping a TypeError
    raise DeserializationError(
        error_name="DESERIALIZE_UNSUPPORTED_ANNOTATION",
        label=format_location(location),
        value=annotation,
        problem=f"No deserializer is available for the annotation {annotation!r}.",
        expected=(
            "A primitive, a container, a union, Annotated, Literal, an enum, a dataclass, "
            "a NamedTuple, a TypedDict, a NewType, or a type that is built in or "
            "registered with register_type()."
        ),
        how_to_fix=(
            f"Register a handler: register_type({annotation!r}, from_func=...).",
            "Or use a supported annotation for this field.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_unsupported_annotation_error — Nobody Can Build This

## Purpose
Raised for `Callable[..., int]`, a plain class nobody registered, a protocol. The
mistake is in the annotation, which is why it names the annotation and the place
it was asked for.
"""
