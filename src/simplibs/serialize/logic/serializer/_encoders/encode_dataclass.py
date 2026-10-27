import dataclasses
from typing import Any
# Outers
from ..._common_helpers import get_field_options, Location
from .._classes import SerializeContext
from .._validations import raise_duplicate_key_error


def encode_dataclass(
    obj: Any,
    location: Location,
    context: SerializeContext,
) -> dict[str, Any]:
    """Convert a dataclass instance to a dict of its fields.

    Args:
        obj: A dataclass instance.
        location: Where in the data this value sits.
        context: The state of the current `serialize` call.

    Returns:
        A dict; a field is written under its alias, and left out if excluded.
    """

    result: dict[str, Any] = {}
    for field in dataclasses.fields(obj):

        # 1. The name in the data and whether the field is data at all
        name, exclude = get_field_options(field)
        if exclude:
            continue

        # 2. Two fields with one alias would lose one of them
        if name in result:
            raise_duplicate_key_error(location, name)

        # 3. The value, converted below its name
        result[name] = context.encode(getattr(obj, field.name), (*location, name))

    # 4. Fields in the order they are declared
    return result


_DESIGN_NOTES = """
# encode_dataclass — A Dataclass to a Dict

## Purpose
Fields in declaration order, each under the name it has in the data.

## Alias and Exclusion
Both come from `field(metadata=...)`, normally built with `serialized_field`.
The location uses the name in the data (`$.userName`), because that is what the
reader of the file sees.

## `init=False` Fields Are Written
They are part of the object's state. The way back knows them and does not
require them — see `deserialize`.
"""
