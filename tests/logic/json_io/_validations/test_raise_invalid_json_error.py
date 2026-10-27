import json

import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.json_io._validations import raise_invalid_json_error


def _syntax_error(text: str | bytes) -> json.JSONDecodeError:
    """Produce the real JSONDecodeError json.loads raises for the given text."""
    try:
        json.loads(text)
    except json.JSONDecodeError as err:
        return err
    raise AssertionError(f"{text!r} unexpectedly parsed as JSON")


# The mistake sits in the middle of a text that goes on for a long way after it
_LONG_TEXT = "[" + ",".join(["1"] * 40) + " 2" + ",3" * 30 + "]"

_TEXTS = [
    pytest.param("{'a': 1}", id="single_quotes"),
    pytest.param('{\n  "a": 1\n  "b": 2\n}', id="missing_comma_on_third_line"),
    pytest.param(_LONG_TEXT, id="long_text"),
]


def _assert_card(subtests, json_str, caught, *, problem, value) -> BaseException:
    """Run the raiser and verify the parts of the card that every case shares."""

    def raising_wrapper(target):
        raise_invalid_json_error(target, caught)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(json_str,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_INVALID_JSON",
        label="json_str",
        value=value,
        problem=problem,
        expected="Valid JSON text (UTF-8 if given as bytes).",
        how_to_fix=(
            "Fix the text at the reported position — a missing comma, a trailing comma, "
            "single quotes and unquoted keys are the usual causes.",
            "The value shown is the text around that position.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The card must be catchable as ValueError and keep the original exception as its cause
    assert isinstance(exc, ValueError)
    assert exc.__cause__ is caught
    return exc


@pytest.mark.parametrize("json_str", _TEXTS)
def test_raise_invalid_json_error_syntax_error_in_text(subtests, json_str) -> None:
    """A syntax error in text reports the line, the column and the text around the spot."""
    caught = _syntax_error(json_str)

    exc = _assert_card(
        subtests,
        json_str,
        caught,
        problem=f"The text is not valid JSON at line {caught.lineno}, column {caught.colno}: {caught.msg}.",
        value=json_str[max(0, caught.pos - 20):caught.pos + 20],
    )

    # The excerpt is a window of at most forty characters, never the whole text
    assert len(exc.value) <= 40


def test_raise_invalid_json_error_syntax_error_in_bytes(subtests) -> None:
    """Bytes get the same position in the message, but no excerpt of the text."""
    json_bytes = b"{'a': 1}"
    caught = _syntax_error(json_bytes)

    _assert_card(
        subtests,
        json_bytes,
        caught,
        problem=f"The text is not valid JSON at line {caught.lineno}, column {caught.colno}: {caught.msg}.",
        value=None,
    )


def test_raise_invalid_json_error_bad_utf8_bytes(subtests) -> None:
    """Bytes that are not UTF-8 have no position, only a reason."""
    json_bytes = b'"\xff"'
    try:
        json_bytes.decode("utf-8")
    except UnicodeDecodeError as err:
        caught = err
    else:
        raise AssertionError("the bytes unexpectedly decoded as UTF-8")

    _assert_card(
        subtests,
        json_bytes,
        caught,
        problem=f"The text could not be read as JSON: {caught}.",
        value=None,
    )


def test_raise_invalid_json_error_too_deep(subtests) -> None:
    """Text nested beyond the interpreter's limit gets its own wording."""
    caught = RecursionError("maximum recursion depth exceeded")

    _assert_card(
        subtests,
        "[" * 10,
        caught,
        problem="The text is nested so deeply that it cannot be read.",
        value=None,
    )
