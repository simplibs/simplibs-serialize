from .convert.Deserialize import Deserialize
from .convert.Serialize import Serialize
from .destinations.DumpJsonFileTo import DumpJsonFileTo
from .files.DumpJsonFile import DumpJsonFile
from .files.LoadJsonFile import LoadJsonFile
from .text.FromJson import FromJson
from .text.ToJson import ToJson


__all__ = [
    # convert — structures
    "Serialize",
    "Deserialize",
    # text — JSON as a string
    "ToJson",
    "FromJson",
    # files — JSON on disk (the object flows in, the path is configuration; and the reverse)
    "DumpJsonFile",
    "LoadJsonFile",
    # destinations — the path flows in, the object is configuration
    "DumpJsonFileTo",
]


_DESIGN_NOTES = """
# Serialize Actions Sub-Package

## Purpose
The functions of the library that take one main value and return one result, as
`Action`s: constructed once with their options, then called with the main input
and chainable with `>>`, `&` and `|`.

```python
pipeline = (
    ReadJson()                                  # simplibs.file.actions
    >> Deserialize(annotation=Config)           # dict -> Config
    >> some_transformation
    >> DumpJsonFile(path="out/config.json")     # Config -> file
)
```

## Two Directions for the File Writer
A writer needs a path AND an object, and a pipeline carries one value. As in
`simplibs-file`, both are offered:

* `DumpJsonFile(path=...)(obj)` — the OBJECT flows, the path is configuration.
  The usual case.
* `DumpJsonFileTo(obj=...)(path)` — the PATH flows, the object is configuration:
  the same default settings written to every path of a list.

## What Is Not Here
* **`is_serializable`, `is_deserializable`:** they are Rules (`IsSerializable`,
  `IsDeserializable` in `simplibs.serialize.rules`) and already work as pipeline
  steps — a pass-through guard.
* **`register_type`, `unregister_type`:** set-up of the library, not a step of
  data flow.

## Domain Folder
`actions/` has its own `__all__` and is not re-exported from the package root,
exactly like the actions of the other libraries.

## Internal Components Registry

| Component        | Type   | Description                                                    |
| :--------------- | :----- | :------------------------------------------------------------- |
| `Serialize`      | Action | Object in, JSON-compatible structure out.                      |
| `Deserialize`    | Action | Structure in, an object of the configured annotation out.      |
| `ToJson`         | Action | Object in, JSON text out.                                      |
| `FromJson`       | Action | JSON text in, an object of the configured annotation out.      |
| `DumpJsonFile`   | Action | Object in, written to the configured path; the `Path` out.     |
| `LoadJsonFile`   | Action | Path in, the file's content built into the configured type out. |
| `DumpJsonFileTo` | Action | Path in, the configured object written there; the `Path` out.  |
"""
