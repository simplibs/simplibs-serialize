from collections.abc import Callable
from typing import Any, TypeAlias


FromHandler: TypeAlias = Callable[[Any, Any], Any]
"""A function `from_func(data, annotation)` that builds an object back from data."""


_DESIGN_NOTES = """
# FromHandler — The Shape of `from_func`

## Purpose
One name for "the function you pass as `from_func` to `register_type`".

## The Second Argument Is the Annotation
The handler receives the annotation it was found for, not only the data. The
same handler therefore serves a whole family of classes found through their base
class: `lambda data, target: target(data)` builds a `PosixPath`, a `WindowsPath`
or any `Path` subclass the caller asked for.

## `Any`, Not `type`
A handler can also be registered for a subscripted annotation such as `list[int]`,
which is not a `type`, so the second parameter is `Any`.
"""
