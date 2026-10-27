import types
import typing
from collections import OrderedDict, deque
from collections import abc
from collections.abc import Mapping
from typing import Any, Final
# Inners
from .build_annotated_value import build_annotated_value
from .build_elements_value import build_elements_value
from .build_literal_value import build_literal_value
from .build_mapping_value import build_mapping_value
from .build_qualified_value import build_qualified_value
from .build_tuple_value import build_tuple_value
from .build_union_value import build_union_value


_TABLE: dict[Any, Any] = {
    # ---- ELEMENTS — a list of items -------------------------------------
    list: build_elements_value,
    set: build_elements_value,
    frozenset: build_elements_value,
    deque: build_elements_value,
    abc.Sequence: build_elements_value,
    abc.MutableSequence: build_elements_value,
    abc.Collection: build_elements_value,
    abc.Iterable: build_elements_value,
    abc.Set: build_elements_value,
    abc.MutableSet: build_elements_value,

    # ---- TUPLE — bare, homogeneous or positional -------------------------
    tuple: build_tuple_value,

    # ---- MAPPING — an object with typed keys and values ------------------
    dict: build_mapping_value,
    OrderedDict: build_mapping_value,
    abc.Mapping: build_mapping_value,
    abc.MutableMapping: build_mapping_value,

    # ---- UNION — Union[...], X | Y, Optional[X] --------------------------
    typing.Union: build_union_value,
    types.UnionType: build_union_value,

    # ---- ANNOTATED, LITERAL ------------------------------------------------
    typing.Annotated: build_annotated_value,
    typing.Literal: build_literal_value,

    # ---- QUALIFIERS — transparent wrappers --------------------------------
    typing.Final: build_qualified_value,
    typing.Required: build_qualified_value,
    typing.NotRequired: build_qualified_value,
}

# `ReadOnly` exists from Python 3.13 on
if hasattr(typing, "ReadOnly"):
    _TABLE[typing.ReadOnly] = build_qualified_value

BUILDER_TABLE: Final[Mapping[Any, Any]] = types.MappingProxyType(_TABLE)
"""Read-only table: the origin of an annotation (`list` for `list[int]`) → its builder."""


_DESIGN_NOTES = """
# BUILDER_TABLE — Which Builder for Which Annotation

## Purpose
One table instead of a ladder of `if`s, keyed by `get_origin(annotation)`
(`list[int]` → `list`) or, for an annotation without arguments, by the
annotation itself (`list` → `list`). So a bare `list` and `list[int]` reach the
same builder, and the builder asks for the arguments.

## Not in the Table
Dataclasses, `NamedTuple`, `TypedDict`, `NewType` and `type` aliases have no
origin to key by — `build_value` recognizes them by what they are.
"""
