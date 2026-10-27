from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_to_func_needs_class_error(
    type_: Any
) -> NoReturn:
    """Raise ParamError when `to_func` is given for something that is not a class.

    Args:
        type_: The annotation that was given together with `to_func`.
    """

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="SERIALIZE_REGISTER_TO_FUNC_NEEDS_CLASS",
        label="to_func",
        value=type_,
        problem=(
            "`to_func` is found through the class of the object being serialized, "
            f"so it could never run for {type_!r}."
        ),
        expected="A plain class as `type_` whenever `to_func` is given.",
        how_to_fix=(
            "Register `to_func` on the class itself, e.g. `list` or `Point`.",
            "Keep `from_func` alone for an annotation such as `list[int]`.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_to_func_needs_class_error — A Handler That Could Never Run

## Purpose
`serialize` has only an object in hand, and `type(obj)` is always a class — never
`list[int]`. A `to_func` stored under an annotation would be accepted and then
never called, which is the worst kind of bug: no error and no effect.
"""
