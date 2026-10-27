from simplibs.actions import create_action
# Outers
from ...logic.json_io import to_json


ToJson = create_action(
    to_json,
    main_param="obj",
    class_name="ToJson",
)
"""Action wrapping `to_json` — writes the object flowing in as JSON text."""


_DESIGN_NOTES = """
# ToJson — Action Over `to_json`

## Purpose
`... >> ToJson(indent=None)` — a compact JSON body at the end of a pipeline.

## Shape
Main input: `obj`. Any supported object in, `str` out. Options: `indent`,
`ensure_ascii`, `sort_keys`, `allow_nan`, `default`.
"""
