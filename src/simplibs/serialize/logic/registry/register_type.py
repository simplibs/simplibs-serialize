from typing import Any
from simplibs.validate import validate_call
# Outers
from ...annotations import FromHandler, ToHandler
# Inners
from ._handlers.active import FROM_HANDLERS, TO_HANDLERS
from ._helpers import is_plain_class, is_registrable_type
from ._validations import (
    raise_no_handler_error,
    raise_not_registrable_type_error,
    raise_to_func_needs_class_error,
    raise_unhashable_type_error,
)


@validate_call
def register_type(
    type_: Any,
    *,
    to_func: ToHandler | None = None,
    from_func: FromHandler | None = None,
) -> None:
    """Teach the library a type of your own — or replace a built-in handler.

    Args:
        type_: A class (`Point`), a subscripted annotation (`list[int]`) or a
            `NewType`. A handler registered for a class is used for its
            subclasses as well, unless they have a handler of their own.
        to_func: Called as `to_func(obj)` by `serialize`. It may return
            anything `serialize` itself understands. Needs a class as `type_`.
        from_func: Called as `from_func(data, annotation)` by `deserialize`.

    Raises:
        ParamError: If no handler is given, if `type_` is not a type, is not
            hashable, or if `to_func` is given for something that is not a class.

    Example:
        register_type(
            Point,
            to_func=lambda p: {"x": p.x, "y": p.y},
            from_func=lambda data, cls: cls(data["x"], data["y"]),
        )
    """

    # 1. Nothing to register
    if to_func is None and from_func is None:
        raise_no_handler_error()

    # 2. The key must be something the lookup can ever meet
    if not is_registrable_type(type_):
        raise_not_registrable_type_error(type_)

    # 3. The key must be hashable (a subscripted annotation can carry unhashable metadata)
    try:
        hash(type_)
    except TypeError:
        raise_unhashable_type_error(type_)

    # 4. `to_func` is found by the class of the object, so it needs a class
    if to_func is not None and not is_plain_class(type_):
        raise_to_func_needs_class_error(type_)

    # 5. Store each handler that was given
    if to_func is not None:
        TO_HANDLERS[type_] = to_func
    if from_func is not None:
        FROM_HANDLERS[type_] = from_func


_DESIGN_NOTES = """
# register_type — Teach the Library a Type

## Purpose
The one door through which a custom type enters the registry.

## Replacing a Built-in
Registering `datetime` replaces the built-in handler for it. That is allowed on
purpose (a project that wants epoch seconds instead of ISO text can have them).
"""
