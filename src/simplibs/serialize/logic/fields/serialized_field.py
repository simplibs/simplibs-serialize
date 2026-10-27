import dataclasses
from collections.abc import Mapping
from typing import Any
from simplibs.validate import validate_call
# Outers
from .._constants import FIELD_ALIAS_OPTION, FIELD_EXCLUDE_OPTION, FIELD_METADATA_KEY


@validate_call
def serialized_field(
    *,
    alias: str | None = None,
    exclude: bool = False,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    init: bool = True,
    repr: bool = True,
    hash: bool | None = None,
    compare: bool = True,
    metadata: Mapping[str, Any] | None = None,
    kw_only: Any = dataclasses.MISSING,
) -> Any:
    """Declare a dataclass field with a name of its own in the data, or one that is no data.

    Takes everything `dataclasses.field` takes, plus two options.

    Args:
        alias: The name the field has in the data (`userName` for `user_name`).
        exclude: If True, `serialize` leaves the field out. Give such a field a
            default, otherwise `deserialize` cannot build the object back.
        default: As in `dataclasses.field`.
        default_factory: As in `dataclasses.field`.
        init: As in `dataclasses.field`.
        repr: As in `dataclasses.field`.
        hash: As in `dataclasses.field`.
        compare: As in `dataclasses.field`.
        metadata: As in `dataclasses.field`; the serialize options are added to it.
        kw_only: As in `dataclasses.field`.

    Returns:
        The field, to be assigned in a dataclass body.

    Example:
        @dataclass
        class User:
            user_name: str = serialized_field(alias="userName")
            cache: dict = serialized_field(exclude=True, default_factory=dict)
    """

    # 1. Only the options that were asked for are written down
    options: dict[str, Any] = {}
    if alias is not None:
        options[FIELD_ALIAS_OPTION] = alias
    if exclude:
        options[FIELD_EXCLUDE_OPTION] = True

    # 2. They join the caller's own metadata under one namespaced key
    merged: dict[Any, Any] = dict(metadata) if metadata else {}
    if options:
        merged[FIELD_METADATA_KEY] = options

    # 3. The rest is exactly `dataclasses.field`
    return dataclasses.field(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=merged,
        kw_only=kw_only,
    )


_DESIGN_NOTES = """
# serialized_field — A Field That Knows Its Name in the Data

## Purpose
Foreign formats do not follow Python naming, and some attributes (a cache, an
open handle, a secret) belong to the object but not to the file. Both are said
where the field is declared, in the standard place for it: `field(metadata=...)`.

## Why Not a Second Configuration Object
A mapping from class to renamed fields would live far from the class and drift
from it. The field is the one place that has to change when the class changes.

## Why Not `Annotated` Markers
`Annotated[str, Alias("userName")]` would need `serialize` to read type hints
of every class on every call. The field metadata is read directly and costs
nothing for fields that have none.

## Mirrors `dataclasses.field`
Every parameter is the same, so `serialized_field(default=0)` works as a drop-in
replacement. The two shadowed names (`repr`, `hash`) are `dataclasses.field`'s
own.
"""
