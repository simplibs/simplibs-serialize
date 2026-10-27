from typing import NoReturn
from simplibs.exception import ParamError


def raise_no_handler_error() -> NoReturn:
    """Raise ParamError when register_type is called without any handler."""

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="SERIALIZE_REGISTER_NO_HANDLER",
        label="to_func / from_func",
        problem="register_type() was called without any handler.",
        expected="At least one of `to_func` and `from_func`.",
        how_to_fix=(
            "Pass `to_func` to teach `serialize` this type.",
            "Pass `from_func` to teach `deserialize` this type.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_no_handler_error — A Registration That Registers Nothing

## Purpose
`register_type(Point)` with neither function would silently do nothing, and the
type would then fail much later with a message about an unsupported type. The
mistake is reported where it is made.
"""
