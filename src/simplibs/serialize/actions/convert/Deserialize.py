from simplibs.actions import create_action
# Outers
from ...logic.deserializer import deserialize


Deserialize = create_action(
    deserialize,
    main_param="data",
    class_name="Deserialize",
)
"""Action wrapping `deserialize` — builds the configured `annotation` from the data flowing in."""


_DESIGN_NOTES = """
# Deserialize — Action Over `deserialize`

## Purpose
`ReadJson() >> Deserialize(annotation=Config)` — the file's content becomes a
typed object with its rules checked.

## Shape
Main input: `data`. A structure in, an object of `annotation` out. The
annotation is required configuration; `strict` is the other option.

## One Annotation per Action
The annotation does not flow with the data, because a pipeline carries one
value. `ForEach(Deserialize(annotation=Item))` covers a list of items.
"""
