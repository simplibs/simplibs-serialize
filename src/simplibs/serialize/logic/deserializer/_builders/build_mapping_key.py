from types import NoneType
from typing import Any
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._helpers import key_candidates
from .._validations import raise_invalid_key_error


def build_mapping_key(
    key: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Read one key of a JSON object back as the key type the annotation asks for.

    Args:
        key: The key as it is in the data — text, if the data came from JSON.
        annotation: The key annotation: `str`, `int`, an enum, `date`, a union, ...
        location: The location of the mapping (the key is not part of it).
        context: The state of the current `deserialize` call.

    Returns:
        The key.
    """

    # 1. A key that is not text came from Python data — it is a value like any other
    if not isinstance(key, str):
        return context.build(key, annotation, location)

    # 2. Text for text
    if annotation is str or annotation is Any or annotation is object:
        return key

    # 3. The forms the text can stand for: "1" is 1, "true" is True, "null" is None.
    #    A number never accepts the text itself, so it is not even tried
    candidates = key_candidates(key)
    if annotation in (int, float, bool, NoneType):
        candidates = candidates[1:]

    # 4. The first form the annotation accepts — enums, dates, UUIDs, unions,
    #    `Annotated` rules and handlers all decide for themselves
    for candidate in candidates:
        try:
            return context.build(candidate, annotation, location)
        except DeserializationError:
            continue

    # 5. No form fits
    raise_invalid_key_error(location, annotation, key)


_DESIGN_NOTES = """
# build_mapping_key — Text Back to a Key

## Purpose
`serialize` writes a key as text the way `json.dumps` does (`1` → `"1"`,
`True` → `"true"`, `None` → `"null"`); this is the inverse, driven by the
annotation.

## Why Candidates
Which type a key text stands for is decided by the annotation, not by the text:
`"1"` is a `str` for `dict[str, X]`, an `int` for `dict[int, X]`, and for an
`IntEnum` the member with value 1. Trying the possible forms through the normal
`build` gets all of those, and every rule, handler and union, for free.

## Unions
`dict[int | str, X]` with the key `"1"` takes the first form that fits — the
"""
