from collections.abc import Mapping
from typing import Any, get_args, get_origin
# Outers
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._validations import raise_build_failed_error, raise_key_collision_error, raise_wrong_type_error
# Inners
from .build_mapping_key import build_mapping_key
from .constants import MAPPING_FACTORIES


def build_mapping_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build a dict, OrderedDict or abstract mapping from an object.

    Args:
        data: The serialized data — an object (dict).
        annotation: `dict[str, int]`, `dict[Color, Point]`, `Mapping[...]`, bare `dict`, ...
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The mapping, keys and values built against their annotations (`Any`
        if the annotation gives none).
    """

    # 1. A JSON object
    if not isinstance(data, Mapping):
        raise_wrong_type_error(location, annotation, data)

    # 2. Key and value annotations, if there are any
    args = get_args(annotation)
    key_annotation, value_annotation = args if len(args) == 2 else (Any, Any)

    # 3. Each key is read back from text, each value is built below its key
    result: dict[Any, Any] = {}
    sources: dict[Any, Any] = {}
    for key, value in data.items():
        built_key = build_mapping_key(key, key_annotation, location, context)
        built_value = context.build(value, value_annotation, (*location, str(key)))
        try:
            # Two texts that become one key must not silently swallow a value
            if built_key in result:
                raise_key_collision_error(location, built_key, sources[built_key], key)
            result[built_key] = built_value
        except TypeError as caught:
            raise_build_failed_error(location, annotation, caught)
        sources[built_key] = key

    # 4. The mapping the annotation asks for
    factory = MAPPING_FACTORIES.get(get_origin(annotation) or annotation)
    return factory(result) if factory is not None else result


_DESIGN_NOTES = """
# build_mapping_value — An Object Becomes a Mapping

## Purpose
Both halves of every entry are built: the key from its text, the value from its
data.

## Location
A value is located by its key (`$.limits.max`); a key that is not text (data that
did not come from JSON) is shown as text.
"""
