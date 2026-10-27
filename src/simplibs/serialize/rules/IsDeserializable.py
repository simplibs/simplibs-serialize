from typing import Any
from simplibs.rules import Rule
# Outers
from ..annotations import TargetType
from ..exceptions import DeserializationError
from ..logic.deserializer import deserialize, is_deserializable
from ..logic._common_helpers import describe_annotation
# Inners
from ._validations import raise_rule_param_invalid_error


class IsDeserializable(Rule):
    """Data must be buildable into the given annotation.

    Rule:
        is_deserializable(value, annotation, strict=...)

    Example:
        validate(raw_config, IsDeserializable(Config))
        gate = IsDeserializable(list[Item], strict=False)
    """

    __slots__ = ("annotation", "strict")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, annotation: TargetType, *, strict: bool = True) -> None:

        # 1. Parameter validation
        if not isinstance(strict, bool):
            raise_rule_param_invalid_error(
                "IsDeserializable", "strict", strict, "a bool", exception=TypeError,
            )

        # 2. Parameter assignment
        self.annotation = annotation
        self.strict = strict

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. The real build, discarded — the rule cannot disagree with `deserialize`
        return is_deserializable(value, self.annotation, strict=self.strict)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. A noun phrase with the annotation in it
        return f"data for {describe_annotation(self.annotation)}"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Build again to find out exactly what is wrong and where
        reason: DeserializationError | None = None
        try:
            deserialize(value, self.annotation, strict=self.strict)
        except DeserializationError as caught:
            reason = caught

        # 2. The card names the checked value; the precise reason is its cause
        wanted = describe_annotation(self.annotation)
        where = f"{context}: " if context else ""
        exception = DeserializationError(
            error_name="IS_DESERIALIZABLE_ERROR",
            label=value_name or "value",
            value=value,
            problem=f"{where}The data cannot be built into {wanted}; see the cause for the exact location.",
            expected=f"Data that fits {wanted}.",
            how_to_fix=(
                "Correct the part named by the cause.",
                "Or pass strict=False to ignore keys the type does not know.",
            ),
            exception=ValueError,
        )
        exception.__cause__ = reason
        return exception


_DESIGN_NOTES = """
# IsDeserializable — Fit to Be Read

## Purpose
A gate in front of `Deserialize(annotation=...)` or `FromJson(...)`: data that
does not fit is stopped — or sent down a fallback branch with `|` — before the
real build, and `IsDeserializable(Config)` reads as what it checks.

## Delegates to `is_deserializable`
One definition of "deserializable": the function. The rule only wraps it.

## The Cause Carries the Details
`build_exception` repeats the build and attaches the real `DeserializationError`
(with its `$.servers[2].port` location) as the cause of the card.

## Parameters
`annotation` is the first parameter and is not checked: any annotation is
acceptable to the rule, an unsupported one simply never fits. `strict` is validated by hand.

## Description
`describe()` returns "data for <annotation>", where the annotation is described
in the same words the failure cards use.
"""
