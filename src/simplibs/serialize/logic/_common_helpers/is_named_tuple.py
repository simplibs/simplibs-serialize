from typing import Any
# Inners
from .is_named_tuple_class import is_named_tuple_class


def is_named_tuple(
    obj: Any
) -> bool:
    """Return True for an instance of a NamedTuple or a `collections.namedtuple`.

    Args:
        obj: Anything.
    """
    # 1. The question is asked once, about the class
    return is_named_tuple_class(type(obj))


_DESIGN_NOTES = """
# is_named_tuple — A Tuple With Names

## Purpose
Tell an instance of a `NamedTuple` from a plain tuple: the serializer writes the first
as an object (its field names are the keys) and the second as a list.

## Logic
Delegates to `is_named_tuple_class(type(obj))`, so the rule "what is a named tuple"
exists in one place only.
"""
