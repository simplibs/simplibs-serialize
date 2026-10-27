from typing import Any


def is_named_tuple_class(
    cls: Any
) -> bool:
    """Return True for the class made by `NamedTuple` or `collections.namedtuple`.

    Args:
        cls: Anything.
    """

    # 1. A tuple class with named fields
    return (
        isinstance(cls, type)
        and issubclass(cls, tuple)
        and hasattr(cls, "_fields")
        and hasattr(cls, "_asdict")
    )


_DESIGN_NOTES = """
# is_named_tuple_class — The Class Side of `is_named_tuple`

## Purpose
`serialize` has an instance in hand, `deserialize` only the annotation.
"""
