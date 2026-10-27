from types import NoneType
from typing import Any, get_args
# Outers
from ....exceptions import DeserializationError
from ..._common_helpers import Location
from .._classes import DeserializeContext
from .._helpers import closest_failure, is_exact_type_match
from .._validations import raise_union_ambiguous_error, raise_union_no_match_error


def build_union_value(
    data: Any,
    annotation: Any,
    location: Location,
    context: DeserializeContext,
) -> Any:
    """Build data against a union: `Union[A, B]`, `A | B`, `Optional[A]`.

    Args:
        data: The serialized data at this location.
        annotation: The union annotation.
        location: Where in the data this value sits.
        context: The state of the current `deserialize` call.

    Returns:
        The value built against the member that fits.
    """

    # 1. None is decided first: it belongs to the union, or the union has no answer
    members = get_args(annotation)
    if data is None:
        if NoneType in members:
            return None
        raise_union_no_match_error(location, annotation, data)

    # 2. `Optional[X]` is no choice: with None out of the way X is the only member,
    #    and its own error (with the deep location) is the one worth showing
    candidates = [member for member in members if member is not NoneType]
    if len(candidates) == 1:
        return context.build(data, candidates[0], location)

    # 3. Every member is tried; a member that cannot build the data is not a candidate
    matches: list[tuple[Any, Any]] = []
    failures: list[DeserializationError] = []
    for member in candidates:
        try:
            matches.append((member, context.build(data, member, location)))
        except DeserializationError as caught:
            failures.append(caught)

    # 4. One candidate — the answer; none — no member fits
    if len(matches) == 1:
        return matches[0][1]
    if not matches:
        raise_union_no_match_error(location, annotation, data, closest_failure(failures))

    # 5. Several fit: the member that is exactly the data's own JSON type wins
    exact = [match for match in matches if is_exact_type_match(data, match[0])]
    if len(exact) == 1:
        return exact[0][1]

    # 6. A real tie
    raise_union_ambiguous_error(location, annotation, data, [member for member, _ in matches])


_DESIGN_NOTES = """
# build_union_value — Which Member Is Meant

## Purpose
`int | str`, `Point | None`, `list[int] | dict[str, int]`.

## Exact Match Breaks a Tie
A float fits `int | float` only as `float` — but an int fits both (an int is a
fine float). `5` is an `int`; `5.0` a `float`. `"2024-01-02"` fits `str | date` as
both; the `str`, being exactly the data's type, wins. For `date | str` where the
`date` is wanted, write `date | None` and keep the text out of the union.

## `Optional[X]` Is Not a Choice
`X | None` has one real member. Data that is not `None` is built as `X` straight away,
and `X`'s own error — `$.pt.x`, not just `$.pt` — is the one the caller sees.

## No Member Fits
The card names the union at its own location; the failure of the member that got
deepest into the data (`closest_failure`) is attached as the cause, so the traceback
still says why.

## Only a Real Tie Is an Error
`list[int] | list[str]` with `[]` is a tie — and says so, with the members that
fit.

## Dates: `date | datetime`
`datetime.fromisoformat("2026-10-24")` succeeds (midnight), so for that text both members
fit, neither is an exact primitive match, and the union is reported as ambiguous. Put the
member the data really is in the annotation, or write `datetime` alone.
"""
