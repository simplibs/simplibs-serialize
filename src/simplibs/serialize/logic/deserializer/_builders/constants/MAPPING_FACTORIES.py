from collections import OrderedDict
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Final


MAPPING_FACTORIES: Final[Mapping[Any, type]] = MappingProxyType({
    OrderedDict: OrderedDict,
})
"""Origin → how to turn the built dict into the mapping. Everything else is a `dict`."""


_DESIGN_NOTES = """
# MAPPING_FACTORIES — What the Entries Become

## Purpose
`build_mapping_value` builds a plain dict first; an origin listed here turns it
into its own kind. `dict`, `Mapping` and `MutableMapping` stay a `dict`.

## No `defaultdict`
A `defaultdict` needs a default factory the annotation does not carry.
Register a handler for it (`register_type`) if one is needed.
"""
