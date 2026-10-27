from collections import deque
from collections import abc
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Final


ELEMENT_FACTORIES: Final[Mapping[Any, type]] = MappingProxyType({
    set: set,
    frozenset: frozenset,
    deque: deque,
    abc.Set: frozenset,
    abc.MutableSet: set,
})
"""Origin → how to turn the built items into the container. Everything else is a `list`."""


_DESIGN_NOTES = """
# ELEMENT_FACTORIES — What the Items Become

## Purpose
`build_elements_value` builds a list of items first; this table says what that
list is turned into. An origin that is not here (`list`, `Sequence`, `Iterable`,
`Collection`, ...) stays a `list`.

## The Abstract Set
`collections.abc.Set` promises no mutation, so the immutable `frozenset` is
the honest answer; `MutableSet` gets a `set`.
"""
