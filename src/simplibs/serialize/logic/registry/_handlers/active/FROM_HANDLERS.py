from typing import Any, Final
# Outers
from .....annotations import FromHandler
from ..builtin import BUILTIN_FROM_HANDLERS


FROM_HANDLERS: Final[dict[Any, FromHandler]] = dict(BUILTIN_FROM_HANDLERS)
"""The live table: annotation → `from_func`. Starts as a copy of the built-in handlers."""


_DESIGN_NOTES = """
# FROM_HANDLERS — The Live `from_func` Table

## Purpose
What `deserialize` actually consults. A copy, so that `register_type` can write
into it while `BUILTIN_FROM_HANDLERS` stays what it was shipped as.
"""
