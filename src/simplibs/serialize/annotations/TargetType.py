from typing import Any, TypeAlias


TargetType: TypeAlias = Any
"""A class or typing construct for `deserialize` to build: `Point`, `list[int]`, `int | None`."""


_DESIGN_NOTES = """
# TargetType — The Annotation Passed to `deserialize`

## Purpose
`type[T]` is wrong for `list[int]` or `int | None` — neither is a class — so the
parameter had no honest name. This alias is the name.

## Why `Any`
Python has no type that means "any annotation". The alias keeps the signature
readable and makes the real limit visible in one place: what `deserialize`
supports is documented there, not in the type.
"""
