from typing import Any
from simplibs.validate import validate_call
# Inners
from ._handlers.active import FROM_HANDLERS, TO_HANDLERS
from ._handlers.builtin import BUILTIN_FROM_HANDLERS, BUILTIN_TO_HANDLERS
from ._helpers import reset_handler


@validate_call
def unregister_type(type_: Any) -> bool:
    """Remove the registration of a type, in both directions.

    A built-in handler that `register_type` had replaced comes back. A type the
    library knows nothing about is simply forgotten.

    Args:
        type_: The same class or annotation that was given to `register_type`.

    Returns:
        True if anything changed, False if there was nothing to remove or restore.

    Example:
        register_type(Point, to_func=..., from_func=...)
        ...
        unregister_type(Point)   # the table is as it was before
    """

    # 1. Both directions are reset — never stop after the first one
    to_changed = reset_handler(TO_HANDLERS, BUILTIN_TO_HANDLERS, type_)
    from_changed = reset_handler(FROM_HANDLERS, BUILTIN_FROM_HANDLERS, type_)

    # 2. Report whether the table differs from before the call
    return to_changed or from_changed


_DESIGN_NOTES = """
# unregister_type — Put the Table Back

## Purpose
A registration is global, so a test that registers a type must be able to take
it away again — and a project that replaced a built-in handler must be able to
return to the default.

## Not an Error to Call Twice
Unregistering something that is not registered returns `False` and raises
nothing. A test teardown runs whether or not the test got far enough to
register, so it must be safe to run twice.

## Both Directions at Once
`register_type` can set only one handler, but a half-removed type is only
confusing. Unregistering resets both sides.
"""
