from typing import Any, NoReturn
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import format_location, Location


def raise_rule_failed_error(
    location: Location,
    rule: Any,
    value: Any
) -> NoReturn:
    """Raise DeserializationError when a rule in `Annotated` is not satisfied.

    Args:
        location: Where in the data the value sits.
        rule: The `Rule` or predicate that failed.
        value: The value that was built and then refused.
    """

    # 1. What the rule requires, in the rule's own words where it has them
    try:
        required = rule.describe()
    except Exception:
        required = getattr(rule, "__name__", None) or repr(rule)

    # 2. Raise structured DeserializationError wrapping a ValueError
    raise DeserializationError(
        error_name="DESERIALIZE_RULE_FAILED",
        label=format_location(location),
        value=value,
        problem=f"The value {value!r} does not satisfy the rule: {required}.",
        expected=str(required),
        how_to_fix=("Correct the data so that it satisfies the rule of the type.",),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_rule_failed_error — The Type Said No

## Purpose
`Annotated[int, greater_than(0)]` (and every type from `simplibs-types`) refused
the value that was read. The card is a `DeserializationError` with the
location, not a separate `ValidateError`, so one `except` covers a bad file.
"""
