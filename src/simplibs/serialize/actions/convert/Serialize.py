from simplibs.actions import create_action
# Outers
from ...logic.serializer import serialize


Serialize = create_action(
    serialize,
    main_param="obj",
    class_name="Serialize",
)
"""Action wrapping `serialize` — converts the object flowing in to a JSON-compatible structure."""


_DESIGN_NOTES = """
# Serialize — Action Over `serialize`

## Purpose
`... >> Serialize(default=repr) >> some_step` where a structure is needed in the
middle of a pipeline.

## Shape
Main input: `obj`. Any supported object in, a JSON-compatible structure out
(only `None`, `bool`, `int`, `float`, `str`, `list` and `dict`). Options:
`default`, `allow_nan`.
"""
