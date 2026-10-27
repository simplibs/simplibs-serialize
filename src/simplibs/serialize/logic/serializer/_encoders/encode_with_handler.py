from collections.abc import Callable
from typing import Any
# Outers
from ....exceptions import SerializeError
from ..._common_helpers import Location
from .._classes import SerializeContext
from .._validations import raise_handler_failed_error


def encode_with_handler(
    handler: Callable[[Any], Any],
    obj: Any,
    location: Location,
    context: SerializeContext,
) -> Any:
    """Call a handler and convert what it returns.

    Args:
        handler: A registered `to_func` or the caller's `default`.
        obj: The value the handler is called with.
        location: Where in the data this value sits.
        context: The state of the current `serialize` call.

    Returns:
        The JSON-compatible form of the handler's result.
    """

    # 1. Call it; whatever it raises becomes a card that says where and for what
    try:
        result = handler(obj)
    except (SerializeError, RecursionError):
        raise
    except Exception as caught:
        raise_handler_failed_error(location, obj, caught)

    # 2. The result is converted again, so a handler may return a dict
    #    that holds dates, an enum member, a dataclass...
    return context.encode(result, location)


_DESIGN_NOTES = """
# encode_with_handler — One Handler Call

## Purpose
The same few lines serve the registered handlers and the caller's `default`:
call, wrap a failure, convert the result.

## Why the Result Is Converted Again
A `to_func` can stay one line long (`lambda p: {"when": p.when, "who": p.who}`)
because the library converts what it returns. A handler that returns its own
argument, or a new value of its own type each time, is a circle — the guard or
the too-deep card names it.

## Which Errors Pass Through
* Library errors (`SerializeError`) are already cards with a location.
* `RecursionError` is not the handler's fault; the top of `serialize` handles it.
Everything else a handler raises is wrapped, with the original as its cause.
"""
