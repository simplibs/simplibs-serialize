from typing import Any
# Outers
from ..._constants import JSON_PRIMITIVES


def is_exact_type_match(
    data: Any,
    member: Any
) -> bool:
    """Return True if the data is exactly the primitive the union member names.

    Args:
        data: The serialized data.
        member: One member of a union annotation.
    """

    # 1. Only primitives have an "exact" type: `5` is an `int`, `"x"` is a `str`
    return member in JSON_PRIMITIVES and type(data) is member


_DESIGN_NOTES = """
# is_exact_type_match — The Tie-Breaker of a Union

## Purpose
`5` fits `int` and `float`, `"x"` fits `str` and `Path`. The member that is
exactly what the data is wins; for everything else (lists, objects) no member is
"more exact", and a tie is reported.
"""
