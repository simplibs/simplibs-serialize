from simplibs.actions import create_action
# Outers
from ...logic.json_io import dump_json_file


DumpJsonFileTo = create_action(
    dump_json_file,
    main_param="path",
    class_name="DumpJsonFileTo",
)
"""Action wrapping `dump_json_file` — writes the configured `obj` to the path flowing in."""


_DESIGN_NOTES = """
# DumpJsonFileTo — Action Over `dump_json_file`

## Purpose
The same default settings written to every path of a list:
`ForEach(DumpJsonFileTo(obj=Settings()))`.

## Shape
Main input: `path`. A path in, the written `Path` out. Sibling of `DumpJsonFile`.

## Changes the Disk
This action writes, copies, moves or deletes.
"""
