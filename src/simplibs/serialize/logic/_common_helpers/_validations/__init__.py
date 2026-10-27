from .raise_invalid_field_options_error import raise_invalid_field_options_error


_DESIGN_NOTES = """
# Shared Helpers Validations Sub-Package

## Purpose
The one diagnostic raiser the shared helpers need.

## Internal Components Registry

| Component                           | Type     | Description                                                   |
| :---------------------------------- | :------- | :------------------------------------------------------------ |
| `raise_invalid_field_options_error` | Function | A dataclass field with broken serialize options (`ParamError`). |

## Which Error Class
A `ParamError`, not a `SerializationError`: the mistake is in the class definition, not
in the data being converted, and it is raised in both directions.
"""
