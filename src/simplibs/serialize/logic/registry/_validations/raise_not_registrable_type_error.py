from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_not_registrable_type_error(
    type_: Any
) -> NoReturn:
    """Raise ParamError when `type_` is not a class, an annotation or a NewType.

    Args:
        type_: The value that was given as `type_`.
    """

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="SERIALIZE_REGISTER_NOT_A_TYPE",
        label="type_",
        value=type_,
        problem=f"{type_!r} is not a type, so no data could ever be matched to it.",
        expected="A class, a subscripted annotation such as `list[int]`, or a `NewType`.",
        how_to_fix=(
            "Pass the class itself (`Point`), not an instance or its name as a string.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_not_registrable_type_error — A Key Nobody Could Look Up

## Purpose
A handler stored under `"Point"` or under an instance is never found; the
registration would look successful and the type would still fail later.
"""
