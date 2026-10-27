from typing import Any
from simplibs.validate import validate_call
# Outers
from ...annotations import TargetType
from ...exceptions import DeserializationError
# Inners
from .deserialize import deserialize


@validate_call
def is_deserializable(
    data: Any,
    annotation: TargetType,
    *,
    strict: bool = True,
) -> bool:
    """Return True if `deserialize` would succeed for the data, False if not.

    Args:
        data: The serialized data.
        annotation: The type to build.
        strict: The same switch `deserialize` takes.

    Returns:
        True if the data can be built into the annotation, False if it would
        raise `DeserializationError`.
    """

    # 1. Run the real thing — a prediction could disagree with it
    try:
        deserialize(data, annotation, strict=strict)
    except DeserializationError:
        return False

    # 2. Nothing went wrong
    return True


_DESIGN_NOTES = """
# is_deserializable — Ask Before Building

## Purpose
Check a configuration or a message against a type without a `try/except`.

## A Real Run
The same reasoning as `is_serializable`: it performs the build and discards
the result, so it cannot disagree with `deserialize`.

## What It Does Not Hide
Only `DeserializationError` means "no". A `ParamError` (a broken field
declaration) is a bug in the class and passes through.
"""
