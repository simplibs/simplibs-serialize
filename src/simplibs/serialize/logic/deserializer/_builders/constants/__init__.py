from .ELEMENT_FACTORIES import ELEMENT_FACTORIES
from .MAPPING_FACTORIES import MAPPING_FACTORIES


_DESIGN_NOTES = """
# Builders Constants Sub-Package

## Purpose
The two tables that say which container a builder makes at the end.

## Internal Components Registry

| Component           | Type     | Description                                                      |
| :------------------ | :------- | :--------------------------------------------------------------- |
| `ELEMENT_FACTORIES` | Constant | Origin (`set`, `frozenset`, `deque`, ...) → how to make it.      |
| `MAPPING_FACTORIES` | Constant | Origin (`OrderedDict`) → how to make it.                         |
"""
