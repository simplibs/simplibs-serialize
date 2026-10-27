from .FROM_HANDLERS import FROM_HANDLERS
from .TO_HANDLERS import TO_HANDLERS


_DESIGN_NOTES = """
# Active Handlers Sub-Package

## Purpose
The two live tables. Each starts as a copy of its built-in table and then
carries every `register_type` call.

## Internal Components Registry

| Component       | Type     | Description                                            |
| :-------------- | :------- | :----------------------------------------------------- |
| `TO_HANDLERS`   | Constant | Class → `to_func`, consulted by `find_to_handler`.     |
| `FROM_HANDLERS` | Constant | Annotation → `from_func`, consulted by `find_from_handler`. |
"""
