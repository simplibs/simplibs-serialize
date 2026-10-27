from typing import Any, get_origin
from simplibs.rules import IsTyping


def describe_annotation(
    annotation: Any
) -> str:
    """Describe an annotation in a few words, the way the rules of simplibs do.

    Args:
        annotation: A class or a typing construct.

    Returns:
        For example `list[int] | None`; the plain name of a class; `repr` of
        anything the rule engine cannot describe.
    """

    # 1. The rule engine already knows how to say it: `list[int] | set[int] | str`
    try:
        return IsTyping(annotation).describe()
    except Exception:
        pass

    # 2. A plain class by its name, anything else as it is written
    if isinstance(annotation, type) and get_origin(annotation) is None:
        return annotation.__name__
    return repr(annotation)


_DESIGN_NOTES = """
# describe_annotation — What Was Asked For, in Words

## Purpose
A card that says "expected `Point`" or "expected `list[int] | None`" is read in
one glance; `typing.Optional[list[int]]` and `<class 'main.Point'>` are not.

## Same Words as the Rest of simplibs
`IsTyping(...).describe()` is what `validate_call` prints, so a failed call and a
failed `deserialize` speak alike.

## Never Fails
A card is built on the way to an error; it must not raise another one. Whatever
the rule engine cannot describe falls back to a plain name or `repr`.
"""
