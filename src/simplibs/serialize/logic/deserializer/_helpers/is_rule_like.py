from typing import Any
from simplibs.rules import Rule


def is_rule_like(
    item: Any
) -> bool:
    """Return True if an item of `Annotated` metadata is a rule or a predicate.

    Args:
        item: One item of the metadata of `Annotated[T, ...]`.
    """

    # 1. A `Rule`, or a function that takes the value and says yes or no.
    #    A class (a marker type) is callable but is not a predicate
    return isinstance(item, Rule) or (callable(item) and not isinstance(item, type))


_DESIGN_NOTES = """
# is_rule_like — Whose Metadata Is This

## Purpose
`Annotated` carries anything: documentation text, markers of other libraries,
rules. Only what `validated_type` itself accepts as a rule is checked here; the
rest is not ours to interpret.
"""
