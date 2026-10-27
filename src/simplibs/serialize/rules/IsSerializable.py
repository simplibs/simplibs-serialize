from typing import Any
from simplibs.rules import Rule
# Outers
from ..annotations import ToHandler
from ..exceptions import SerializationError
from ..logic.serializer import is_serializable, serialize
# Inners
from ._validations import raise_rule_param_invalid_error


class IsSerializable(Rule):
    """Value must be convertible by `serialize`.

    Rule:
        is_serializable(value, default=..., allow_nan=...)

    Example:
        validate(payload, IsSerializable())
        guard = IsSerializable(default=repr) & ~IsNone()
    """

    __slots__ = ("default", "allow_nan")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *, default: ToHandler | None = None, allow_nan: bool = False) -> None:

        # 1. Parameter validation
        if default is not None and not callable(default):
            raise_rule_param_invalid_error(
                "IsSerializable", "default", default, "a function or None", exception=TypeError,
            )
        if not isinstance(allow_nan, bool):
            raise_rule_param_invalid_error(
                "IsSerializable", "allow_nan", allow_nan, "a bool", exception=TypeError,
            )

        # 2. Parameter assignment
        self.default = default
        self.allow_nan = allow_nan

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. The real conversion, discarded — the rule cannot disagree with `serialize`
        return is_serializable(value, default=self.default, allow_nan=self.allow_nan)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "serializable value"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Run the conversion again to find out exactly what is wrong and where
        reason: SerializationError | None = None
        try:
            serialize(value, default=self.default, allow_nan=self.allow_nan)
        except SerializationError as caught:
            reason = caught

        # 2. The card names the checked value; the precise reason is its cause
        where = f"{context}: " if context else ""
        exception = SerializationError(
            error_name="IS_SERIALIZABLE_ERROR",
            label=value_name or "value",
            value=value,
            problem=f"{where}The value cannot be converted by serialize(); see the cause for the exact location.",
            expected="A value serialize() can convert.",
            how_to_fix=(
                "Fix the part named by the cause (a type to register, a cycle, a NaN).",
                "Or pass `default=` to deal with unknown objects in one place.",
            ),
            exception=TypeError,
        )
        exception.__cause__ = reason
        return exception


_DESIGN_NOTES = """
# IsSerializable — Fit to Be Written

## Purpose
A gate in front of `ToJson()`, `DumpJsonFile(...)` or an API call: a value that
cannot be written is stopped before the first side effect, and `|` can send it
to a fallback.

## Delegates to `is_serializable`
One definition of "serializable": the function. The rule only wraps it.

## The Cause Carries the Details
`build_exception` runs the conversion once more and attaches the real
`SerializationError` (with its `$.items[2]` location) as the cause of a card that
names the value, as every rule's failure card does.

## Parameters
`default` and `allow_nan` are the function's, validated here by hand (rules are
classes, not `@validate_call` functions).

## Description
`describe()` returns "serializable value" — a short noun phrase that containers
compose into larger texts.
"""
