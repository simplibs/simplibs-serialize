from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
# Outers
from ..._common_helpers import Location


@dataclass(slots=True)
class DeserializeContext:
    """Everything one `deserialize` call carries from step to step.

    Attributes:
        strict: Whether unknown keys are an error.
        build_value: The dispatcher that builds one value.
    """

    strict: bool
    build_value: Callable[[Any, Any, Location, "DeserializeContext"], Any]

    def build(self, data: Any, annotation: Any, location: Location) -> Any:
        """Build one nested value — the way every builder recurses."""

        # 1. Hand the value to the dispatcher together with this context
        return self.build_value(data, annotation, location, self)


_DESIGN_NOTES = """
# DeserializeContext — One Call's Luggage

## Purpose
The twin of `SerializeContext`: what every builder needs (`strict`) and the way
to recurse (`build`).

## `build` Is How Builders Recurse
A builder never imports the dispatcher; that would be a circular import
(`build_value` → `build_elements_value` → `build_value`). It calls
`context.build(data, annotation, location)`, which makes every builder an
independent file that a test can run with a fake context.

## Simpler Than Its Twin
Reading data has no cycle to detect: data is finite, and the annotation
does not change while it is read. The context holds no state that changes.
"""
