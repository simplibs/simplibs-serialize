from typing import TypeAlias


Location: TypeAlias = tuple[str | int, ...]
"""Keys and indexes from the root to one value: `("items", 2, "name")`."""


_DESIGN_NOTES = """
# Location — Where in the Data

## Purpose
Every nested step of `serialize` and `deserialize` knows where it is, so a card
can say `$.items[2].name` instead of only "something is wrong".

## A Tuple, Not a String
A tuple is immutable and cheap to extend with `(*location, key)`; it is turned
into text only when a card is built. Nothing that goes wrong has to be repaired
afterwards, and a key that contains a dot or a bracket cannot confuse it.

## Internal
Not exported from the package root: it is plumbing between the library's own
steps.
"""
