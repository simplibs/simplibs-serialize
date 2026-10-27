from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
# Outers
from ....annotations import ToHandler
from ..._common_helpers import Location


@dataclass(slots=True)
class SerializeContext:
    """Everything one `serialize` call carries from step to step.

    Attributes:
        default: The fallback for an unknown object, or None.
        allow_nan: Whether `nan` and `inf` may pass through.
        encode_value: The dispatcher that converts one value.
        ancestors: The ids of the objects currently being converted, from the
            root down to the present one; a repeated id is a circular reference.
    """

    default: ToHandler | None
    allow_nan: bool
    encode_value: Callable[[Any, Location, "SerializeContext"], Any]
    ancestors: set[int] = field(default_factory=set)

    def encode(self, obj: Any, location: Location) -> Any:
        """Convert one nested value — the way every encoder recurses."""

        # 1. Hand the value to the dispatcher together with this context
        return self.encode_value(obj, location, self)


_DESIGN_NOTES = """
# SerializeContext — One Call's Luggage

## Purpose
`serialize` recurses through lists, dicts and dataclasses. Every step needs the
same few things (the fallback, the `nan` switch, the path taken so far), and
passing four parameters through every encoder would bury what each one does.

## `encode` Is How Encoders Recurse
An encoder never imports the dispatcher: that would be a circular import
(`encode_value` → `encode_mapping` → `encode_value`). It calls
`context.encode(value, location)` instead, so encoders are independent files
that can be tested with a fake context.

## Not Frozen
`ancestors` changes during the walk — an id is added when a value is entered and
removed when it is left — so the context cannot be frozen. A new one is made for
every call, nothing is shared between calls or threads.
"""
