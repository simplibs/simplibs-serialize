from .Location import Location
from .describe_annotation import describe_annotation
from .format_location import format_location
from .get_field_options import get_field_options
from .is_named_tuple import is_named_tuple
from .is_named_tuple_class import is_named_tuple_class


_DESIGN_NOTES = """
# Serialize Shared Helpers Sub-Package

Plain imports, no `__all__` (the package root decides what is public).

## Purpose
What both directions need and neither may own. `serializer` and `deserializer` never
import each other, so everything they share is here — private, not part of the API.

## Internal Components Registry

| Component              | Type     | Description                                                                     |
| :--------------------- | :------- | :------------------------------------------------------------------------------ |
| `Location`             | Alias    | The keys and indexes leading from the root to one value.                        |
| `format_location`      | Function | `("items", 2, "name")` → `$.items[2].name`.                                     |
| `get_field_options`    | Function | The name in the data and the exclusion flag of a dataclass field.               |
| `is_named_tuple`       | Function | True for an instance of a `NamedTuple` or `collections.namedtuple`.             |
| `is_named_tuple_class` | Function | The same question about the class.                                              |
| `describe_annotation`  | Function | An annotation in words, for cards and rule descriptions.                        |
| `_validations`         | Package  | `raise_invalid_field_options_error` — a field declared wrong (`ParamError`).    |

## Why Not `commons`
`commons` holds only what the outside world also uses: the exceptions and the types
written in signatures. A helper used by two internal folders is not that.
"""
