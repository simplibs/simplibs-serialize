_DESIGN_NOTES = """
# Serialize Logic Sub-Package

Nothing is imported or re-exported here: the package root decides what is public.

## Purpose
All the code that does the work, one folder per domain. The layout follows
`simplibs-file`: `logic/` holds the functions, and `actions/`, `rules/` and
`testing/` — the layers built on top of them — stay at the package root.

## Internal Components Registry

| Folder         | Type    | Description                                                                              |
| :------------- | :------ | :--------------------------------------------------------------------------------------- |
| `commons`      | Package | Only what the outside world uses too: the exceptions and the types of signatures.        |
| `_constants`   | Package | Private: the fixed words and groups — JSON primitives, the location root, field options. |
| `_helpers`     | Package | Private: what both directions share — `Location`, `format_location`, field options, ... |
| `registry`     | Package | The table of types known by heart, and `register_type` / `unregister_type` to extend it. |
| `fields`       | Package | `serialized_field` — a dataclass field with an alias or excluded from the data.          |
| `serializer`   | Package | The way out: `serialize` and `is_serializable`, with their encoders.                     |
| `deserializer` | Package | The way back: `deserialize` and `is_deserializable`, with their builders.                |
| `json_io`      | Package | JSON text and files: `to_json`, `from_json`, `dump_json_file`, `load_json_file`.         |

## Direction of Dependencies
Each folder may use only the ones above it in this list:

* `commons`, `_constants` and `_helpers` use nothing of the library but each other
  (`_helpers` uses `_constants`).
* `registry` and `fields` use those three.
* `serializer` and `deserializer` use all of those — and **never each other**.
  Everything both directions need lives in `_helpers` or `_constants`, not in one of them.
* `json_io` is the only folder that uses `serializer` and `deserializer`, and
  the only one that touches `simplibs-file`.

## Private Folders
A leading underscore means "not for the outside". Inside every package the same names
mean the same thing: `_helpers` (small functions), `_validations` (the `raise_*` cards),
`_classes` (state objects), `_constants` (fixed tables).

## Why Two Directions Are Two Folders
The way out decides by the value in hand (`_encoders`), the way back by the
annotation asked for (`_builders`). They share an idea, not code, and keeping
them apart means a change to one cannot quietly change the other.
"""
