from typing import Any, get_origin


def is_plain_class(target: Any) -> bool:
    """Return True for a real class, False for a subscripted annotation or a non-type.

    Args:
        target: Anything that may be a class.
    """

    # 1. `list[int]` is not a class — on some Python versions `isinstance`
    #    claims it is, so the origin is asked as well
    return isinstance(target, type) and get_origin(target) is None


_DESIGN_NOTES = """
# is_plain_class — A Class You Can Walk

## Purpose
`serialize` looks handlers up by `type(obj)` and `find_handler` walks the class
hierarchy. Both need a real class; `list[int]` has no hierarchy of its own, and
an extra check makes the answer the same on every supported Python.
"""
