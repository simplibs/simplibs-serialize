from .encode_dataclass import encode_dataclass
from .encode_items import encode_items
from .encode_mapping import encode_mapping
from .encode_mapping_key import encode_mapping_key
from .encode_structure import encode_structure
from .encode_value import encode_value
from .encode_with_handler import encode_with_handler


_DESIGN_NOTES = """
# Serialize Encoders Sub-Package

## Purpose
One file per kind of value. `encode_value` is the door, `encode_structure`
chooses the kind, the rest do the work.

## Internal Components Registry

| Component             | Type     | Description                                                           |
| :-------------------- | :------- | :-------------------------------------------------------------------- |
| `encode_value`        | Function | Primitives, `None`, the circular-reference guard; else the structure. |
| `encode_structure`    | Function | Chooses the encoder for everything that is not a primitive.           |
| `encode_with_handler` | Function | Runs a handler (registered or `default`) and converts its result.     |
| `encode_items`        | Function | Sequences and sets → list (sets in a fixed order).                    |
| `encode_mapping`      | Function | Any mapping → dict with text keys.                                    |
| `encode_mapping_key`  | Function | One key → the text JSON needs.                                        |
| `encode_dataclass`    | Function | A dataclass instance → dict, honoring field alias and exclusion.      |

## Order of Decisions in `encode_structure`
Handler → primitive subclass → NamedTuple → mapping → dataclass → sequence / set
→ `default` → error. A handler comes first on purpose: a handler a user
registers for their own subclass of `dict` or `list` must win over the general
rule for dicts and lists.
"""
