_DESIGN_NOTES = """
# Registry Handlers Sub-Package

Nothing is imported or re-exported here: each of the two sub-packages is imported by its path.

## Purpose
The tables of handlers, in two layers.

## Internal Components Registry

| Component | Type    | Description                                                                     |
| :-------- | :------ | :------------------------------------------------------------------------------ |
| `builtin` | Package | `BUILTIN_TO_HANDLERS`, `BUILTIN_FROM_HANDLERS` — fixed and read-only.           |
| `active`  | Package | `TO_HANDLERS`, `FROM_HANDLERS` — the live copies; `register_type` writes here.  |

## Why Two Layers
Registering a handler for a type the library already knows replaces the built-in one.
Because the built-in tables never change, `unregister_type` can bring the original
back, and a test can leave the registry exactly as it found it.
"""
