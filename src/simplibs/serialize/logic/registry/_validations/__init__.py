from .raise_no_handler_error import raise_no_handler_error
from .raise_not_registrable_type_error import raise_not_registrable_type_error
from .raise_to_func_needs_class_error import raise_to_func_needs_class_error
from .raise_unhashable_type_error import raise_unhashable_type_error


_DESIGN_NOTES = """
# Registry Validations Sub-Package

## Purpose
Diagnostic raisers for a wrong `register_type` call. They raise `ParamError`:
the mistake is in the code that registers, not in the data.

## Internal Components Registry

| Component                          | Type     | Description                                                |
| :--------------------------------- | :------- | :--------------------------------------------------------- |
| `raise_no_handler_error`           | Function | Neither `to_func` nor `from_func` was given.               |
| `raise_not_registrable_type_error` | Function | `type_` is a string, an instance, ... — not a type.        |
| `raise_unhashable_type_error`      | Function | `type_` cannot be a registry key.                          |
| `raise_to_func_needs_class_error`  | Function | `to_func` was given for something that is not a class.     |
"""
