from collections.abc import Sequence
# Outers
from ....exceptions import DeserializationError


def closest_failure(
    failures: Sequence[DeserializationError]
) -> DeserializationError | None:
    """Return the failure that got furthest into the data, or None if there are none.

    Args:
        failures: The errors of the members of a union that could not build the data.
    """
    # 1. The longer the location text, the deeper the member got before it failed;
    #    on a tie the member listed first wins (max keeps the first of equals)
    if not failures:
        return None
    return max(failures, key=lambda failure: len(str(getattr(failure, "label", "") or "")))


_DESIGN_NOTES = """
# closest_failure — The Member That Almost Fitted

## Purpose
A union that fits nothing says so in one card at its own location. The reason a member
failed is usually deeper (`$.pt.x`), and that is what the reader needs. This picks the
failure that got deepest, so the union card can carry it as its cause.

## Logic
Depth is read from the length of the failure's `label` (the formatted location). A
failure without a `label` counts as depth 0, so nothing breaks if the attribute is absent.
"""
