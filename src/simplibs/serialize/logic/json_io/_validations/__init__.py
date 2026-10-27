from .raise_invalid_json_error import raise_invalid_json_error


_DESIGN_NOTES = """
# JSON I/O Validations Sub-Package

## Purpose
The card for JSON text that cannot be parsed.

## Internal Components Registry

| Component                  | Type     | Description                                     |
| :------------------------- | :------- | :---------------------------------------------- |
| `raise_invalid_json_error` | Function | The text is not valid JSON: where and what.     |
"""
