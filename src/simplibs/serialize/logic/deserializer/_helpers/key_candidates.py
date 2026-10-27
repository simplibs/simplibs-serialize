from typing import Any


def key_candidates(
    text: str
) -> list[Any]:
    """List the forms a JSON key text can stand for, most literal first.

    Args:
        text: A key of a JSON object.

    Returns:
        The text itself, then — where the text is exactly how `json.dumps` writes
        such a value — the `int`, `float`, `bool` or `None` it stands for.
    """

    # 1. The text itself is always possible
    candidates: list[Any] = [text]

    # 2. A whole number written the canonical way: "12", "-3" (not "012", "+1", " 1")
    try:
        number = int(text)
    except ValueError:
        number = None
    if number is not None and str(number) == text:
        candidates.append(number)

    # 3. Any other number: "1.5", "1e-05", "nan" (not "1_0", not with spaces)
    elif text.strip() == text and "_" not in text:
        try:
            candidates.append(float(text))
        except ValueError:
            pass

    # 4. The words JSON uses
    if text == "true":
        candidates.append(True)
    elif text == "false":
        candidates.append(False)
    elif text == "null":
        candidates.append(None)

    return candidates


_DESIGN_NOTES = """
# key_candidates — What a Key Text Might Mean

## Purpose
The inverse of how `serialize` writes keys. Text is all JSON has; the annotation
chooses which of these forms is the right one.

## Canonical Only
`"012"` is not `12`: reading it as `12` would make `"12"` and `"012"` the same
key, and writing it back would give a different file.
"""
