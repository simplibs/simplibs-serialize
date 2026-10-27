from typing import Any, Final
# Outers
from .....annotations import ToHandler
from ..builtin import BUILTIN_TO_HANDLERS


TO_HANDLERS: Final[dict[Any, ToHandler]] = dict(BUILTIN_TO_HANDLERS)
"""The live table: class → `to_func`. Starts as a copy of the built-in handlers."""


_DESIGN_NOTES = """
# TO_HANDLERS — The Live `to_func` Table

## Purpose
What `serialize` actually consults. A copy, so that `register_type` can write
into it while `BUILTIN_TO_HANDLERS` stays what it was shipped as.
"""
