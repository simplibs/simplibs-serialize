from typing import Any, get_args
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext


def build_qualified_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build `Final[T]`, `Required[T]`, `NotRequired[T]` or `ReadOnly[T]`: build `T`.

    Args:
        data: The serialized data at this location.
        annotation: The qualified annotation.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The value built against `T`.
    """

    # 1. A bare qualifier (`x: Final = 5`) names no type: anything goes
    arguments = get_args(annotation)
    inner = arguments[0] if arguments else Any
    # 2. The qualifier says something about the name, not about the value
    return context.build(data, inner, location)


_DESIGN_NOTES = """
# build_qualified_value — A Wrapper That Changes Nothing About the Data

## Purpose
`x: Final[int] = 3` in a dataclass, `Required[int]` in a `TypedDict`: the
wrapper is for type checkers; the data is an `int`.
"""
