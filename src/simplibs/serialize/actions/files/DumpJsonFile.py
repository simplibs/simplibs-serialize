from simplibs.actions import create_action
# Outers
from ...logic.json_io import dump_json_file


DumpJsonFile = create_action(
    dump_json_file,
    main_param="obj",
    class_name="DumpJsonFile",
)
"""Action wrapping `dump_json_file` — writes the object flowing in to the configured `path`."""


_DESIGN_NOTES = """
# DumpJsonFile — Action Over `dump_json_file`

## Purpose
`... >> DumpJsonFile(path="out/config.json", sort_keys=True)` — the end of a
pipeline that produced an object.

## Shape
Main input: `obj`. Any supported object in, the written `Path` out. Sibling:
`DumpJsonFileTo`.

## Changes the Disk
This action writes, copies, moves or deletes.
"""
