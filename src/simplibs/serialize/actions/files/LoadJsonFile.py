from simplibs.actions import create_action
# Outers
from ...logic.json_io import load_json_file


LoadJsonFile = create_action(
    load_json_file,
    main_param="path",
    class_name="LoadJsonFile",
)
"""Action wrapping `load_json_file` — reads the file flowing in and builds the configured `annotation`."""


_DESIGN_NOTES = """
# LoadJsonFile — Action Over `load_json_file`

## Purpose
`ForEach(LoadJsonFile(annotation=Config))` over a list of paths — each file
becomes a typed object, with its rules checked.

## Shape
Main input: `path`. A path in, an object of `annotation` out. The annotation is
required configuration; `strict`, `encoding` and `errors` are the other options.
"""
