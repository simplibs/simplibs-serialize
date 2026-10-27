from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_unhashable_type_error(
    type_: Any
) -> NoReturn:
    """Raise ParamError when `type_` cannot be used as a dict key.

    Args:
        type_: The annotation that is not hashable.
    """

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="SERIALIZE_REGISTER_UNHASHABLE_TYPE",
        label="type_",
        value=type_,
        problem=f"{type_!r} is not hashable, so it cannot be a key of the registry.",
        expected="A hashable class or annotation.",
        how_to_fix=(
            "Register the plain class instead of the annotated one.",
            "Use only hashable objects as the metadata of `Annotated[...]`.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_unhashable_type_error — A Key That Cannot Be a Key

## Purpose
`Annotated[int, [1, 2]]` is a valid annotation but cannot be hashed. The raw
`TypeError: unhashable type` from the table would not say what to change.
"""
