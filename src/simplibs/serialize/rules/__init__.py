from .IsDeserializable import IsDeserializable
from .IsSerializable import IsSerializable

__all__ = [
    "IsDeserializable",
    "IsSerializable",
]


_DESIGN_NOTES = """
# simplibs.serialize.rules — Rules Over Values and Data

## Purpose
The yes/no questions of the library as `Rule`s, so they compose with `&`, `|`, `~`
and work as guard steps in pipelines and in `validate(...)`:

    from simplibs.serialize.rules import IsDeserializable, IsSerializable

    validate(payload, IsSerializable())
    safe = IsDeserializable(Config) >> Deserialize(annotation=Config)

## Domain Folder
`rules/` has its own `__all__` and is not re-exported from the package root,
exactly like the rules of the other libraries.

## Internal Components Registry

| Component         | Type  | Description                                                       |
| :---------------- | :---- | :---------------------------------------------------------------- |
| `IsSerializable`  | Class | Rule: the value can be converted by `serialize`.                  |
| `IsDeserializable`| Class | Rule: the data can be built into the given annotation.            |
"""
