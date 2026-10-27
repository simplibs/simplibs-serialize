from .sort_items import sort_items
from .to_primitive import to_primitive


_DESIGN_NOTES = """
# Serializer Helpers Sub-Package

## Purpose
Small private helpers of the way out: the pieces that are not a decision of their own.
What both directions need (`format_location`, `get_field_options`, ...) is in
`logic/_helpers`.

## Internal Components Registry

| Component      | Type     | Description                                                |
| :------------- | :------- | :--------------------------------------------------------- |
| `sort_items`   | Function | Puts converted set items in a fixed order.                 |
| `to_primitive` | Function | The plain `str` / `int` / `float` inside a subclass of one. |
"""
