from typing import Any
# Outers
from ...annotations import FromHandler
# Inners
from ._handlers.active import FROM_HANDLERS
from ._helpers import find_handler


def find_from_handler(
    annotation: Any
) -> FromHandler | None:
    """Find the handler `deserialize` uses for an annotation.

    Args:
        annotation: The target type: a class or a subscripted annotation.

    Returns:
        The handler registered for the annotation, or for its nearest base
        class if the annotation is a class, or None.
    """

    # 1. Look the annotation up in the live table
    return find_handler(FROM_HANDLERS, annotation)


_DESIGN_NOTES = """
# find_from_handler — The Handler for an Annotation

## Purpose
The only way `deserialize` reaches the registry.
"""
