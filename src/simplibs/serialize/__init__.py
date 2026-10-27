from .annotations import FromHandler, TargetType, ToHandler
from .exceptions import DeserializationError, SerializationError, SerializeError
from .logic.deserializer import deserialize, is_deserializable
from .logic.fields import serialized_field
from .logic.json_io import dump_json_file, from_json, load_json_file, to_json
from .logic.registry import register_type, unregister_type
from .logic.serializer import is_serializable, serialize

__all__ = [
    # Conversion
    "serialize", "deserialize",
    "is_serializable", "is_deserializable",
    # JSON text and files
    "to_json", "from_json",
    "dump_json_file", "load_json_file",
    # Teaching the library a type
    "register_type", "unregister_type",
    # Dataclass fields
    "serialized_field",
    # Exceptions
    "SerializeError", "SerializationError", "DeserializationError",
    # Types for your own signatures
    "TargetType", "ToHandler", "FromHandler",
]


_DESIGN_NOTES = """
# simplibs-serialize — Package Root

## Purpose
Python objects ↔ JSON-compatible structures, JSON text and JSON files, driven by
type annotations. Dataclasses, enums, containers, unions, `Annotated` rules,
dates, paths and your own types; every failure is a card that says where.

## What the Root Exports
Functions and types only — the things you call and the things you write in
signatures. `logic` is plumbing and is imported from the root, not by path.

| Group      | Names                                                                         |
| :--------- | :---------------------------------------------------------------------------- |
| Conversion | `serialize`, `deserialize`, `is_serializable`, `is_deserializable`            |
| JSON       | `to_json`, `from_json`, `dump_json_file`, `load_json_file`                    |
| Types      | `register_type`, `unregister_type`                                            |
| Fields     | `serialized_field`                                                            |
| Errors     | `SerializeError`, `SerializationError`, `DeserializationError`                |
| Hints      | `TargetType`, `ToHandler`, `FromHandler`                         |

## Layout
Four folders and nothing else: `logic` (all the functions), `actions`, `rules` and
`testing` (the layers built on top of them).

## Not Exported From the Root
`actions`, `rules` and `testing` are domain packages: they are imported through their own
folder (`simplibs.serialize.actions`, `simplibs.serialize.rules`,
`simplibs.serialize.testing`), like in the other libraries.
"""
