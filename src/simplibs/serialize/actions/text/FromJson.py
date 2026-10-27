from simplibs.actions import create_action
# Outers
from ...logic.json_io import from_json


FromJson = create_action(
    from_json,
    main_param="json_str",
    class_name="FromJson",
)
"""Action wrapping `from_json` — builds the configured `annotation` from the JSON text flowing in."""


_DESIGN_NOTES = """
# FromJson — Action Over `from_json`

## Purpose
`... >> FromJson(annotation=Message)` — a request body becomes a typed object.

## Shape
Main input: `json_str`. JSON text (or UTF-8 bytes) in, an object of `annotation`
out. The annotation is required configuration; `strict` is the other option.
"""
