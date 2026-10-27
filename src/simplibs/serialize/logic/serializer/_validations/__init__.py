from .raise_circular_reference_error import raise_circular_reference_error
from .raise_duplicate_key_error import raise_duplicate_key_error
from .raise_handler_failed_error import raise_handler_failed_error
from .raise_non_finite_number_error import raise_non_finite_number_error
from .raise_too_deep_error import raise_too_deep_error
from .raise_unsupported_key_error import raise_unsupported_key_error
from .raise_unsupported_type_error import raise_unsupported_type_error


_DESIGN_NOTES = """
# Serializer Validations Sub-Package

## Purpose
Diagnostic raisers for everything that can go wrong on the way out. Each `raise_*`
raises one card: `error_name`, `label` (the location of the value), `value`, `problem`,
`expected`, `how_to_fix`, `exception`.

## Internal Components Registry

| Component                        | Type     | Description                                      |
| :------------------------------- | :------- | :----------------------------------------------- |
| `raise_unsupported_type_error`   | Function | No handler and no rule for the type of a value.  |
| `raise_circular_reference_error` | Function | A value contains itself.                         |
| `raise_non_finite_number_error`  | Function | A `nan` or `inf` where JSON allows neither.      |
| `raise_handler_failed_error`     | Function | A handler (or `default`) raised.                 |
| `raise_duplicate_key_error`      | Function | Two entries would be written under one key.      |
| `raise_unsupported_key_error`    | Function | A key that cannot be written as text.            |
| `raise_too_deep_error`           | Function | Nesting that never ends.                         |

## Which Error Class
Everything that is wrong with the data is a `SerializationError`. The one mistake in
the code (a dataclass field's `metadata`) is a `ParamError` from `logic/_helpers`.
"""
