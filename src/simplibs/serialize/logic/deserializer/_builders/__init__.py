from .BUILDER_TABLE import BUILDER_TABLE
from .constants import ELEMENT_FACTORIES, MAPPING_FACTORIES
from .build_alias_value import build_alias_value
from .build_annotated_value import build_annotated_value
from .build_dataclass_value import build_dataclass_value
from .build_elements_value import build_elements_value
from .build_literal_value import build_literal_value
from .build_mapping_key import build_mapping_key
from .build_mapping_value import build_mapping_value
from .build_named_tuple_value import build_named_tuple_value
from .build_primitive_value import build_primitive_value
from .build_qualified_value import build_qualified_value
from .build_tuple_value import build_tuple_value
from .build_typed_dict_value import build_typed_dict_value
from .build_union_value import build_union_value
from .build_value import build_value
from .build_with_handler import build_with_handler


_DESIGN_NOTES = """
# Serialize Builders Sub-Package

## Purpose
One file per kind of annotation. `build_value` is the door and chooses the
builder; the rest do the work. Every builder has the same signature:
`(data, annotation, location, context)`.

## Internal Components Registry

| Component                 | Type     | Description                                                         |
| :------------------------ | :------- | :------------------------------------------------------------------ |
| `build_value`             | Function | The dispatcher: handler → None → primitive → table → alias → class. |
| `BUILDER_TABLE`           | Constant | Annotation origin → builder (`list`, `dict`, `Union`, `Literal`, ...). |
| `ELEMENT_FACTORIES`       | Constant | Which container `build_elements_value` makes for which origin.      |
| `MAPPING_FACTORIES`       | Constant | Which mapping `build_mapping_value` makes for which origin.         |
| `build_with_handler`      | Function | Runs a registered `from_func` and wraps its failures.               |
| `build_primitive_value`   | Function | `str`, `int`, `float`, `bool` and their subclasses — checked.       |
| `build_elements_value`    | Function | `list`, `set`, `frozenset`, `deque`, `Sequence`, ...                |
| `build_tuple_value`       | Function | Bare, `tuple[T, ...]` and `tuple[A, B]`.                            |
| `build_mapping_value`     | Function | `dict`, `OrderedDict`, `Mapping`, ... with keys read back.          |
| `build_mapping_key`       | Function | A JSON key (text) → the key type of the annotation.                 |
| `build_union_value`       | Function | `X | Y`, `Optional`: exact match first, a tie is an error.         |
| `build_annotated_value`   | Function | `Annotated[T, rule]`: build `T`, then check the rules.              |
| `build_literal_value`     | Function | `Literal[...]`: the data must be one of the listed values.          |
| `build_qualified_value`   | Function | `Final`, `Required`, `NotRequired`, `ReadOnly`: build what is inside. |
| `build_alias_value`       | Function | `NewType`, `type` aliases, `TypeVar`: build what they stand for.    |
| `build_dataclass_value`   | Function | Dataclasses, also generic ones.                                     |
| `build_named_tuple_value` | Function | `NamedTuple`, from an object or a list.                             |
| `build_typed_dict_value`  | Function | `TypedDict`, required and optional keys.                            |
"""
