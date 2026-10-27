from datetime import date

import pytest

from simplibs.serialize import DeserializationError, SerializationError
from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_value, encode_with_handler


def _fake_context():
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_encode_value(obj, location, context):
        calls.append((obj, location))
        return obj

    return SerializeContext(default=None, allow_nan=False, encode_value=fake_encode_value), calls


def _real_context() -> SerializeContext:
    return SerializeContext(default=None, allow_nan=False, encode_value=encode_value)


def test_the_handler_is_called_with_the_object_and_its_result_is_converted_again():
    context, calls = _fake_context()

    result = encode_with_handler(lambda obj: obj + 1, 1, ("items", 0), context)

    assert result == 2
    assert calls == [(2, ("items", 0))]


def test_a_handler_may_return_something_that_needs_converting_itself():
    result = encode_with_handler(
        lambda obj: {"when": date(2026, 1, 2), "tags": {"b", "a"}},
        object(),
        (),
        _real_context(),
    )

    assert result == {"when": "2026-01-02", "tags": ["a", "b"]}


def test_a_failing_handler_becomes_a_card_with_the_original_as_its_cause():
    caught_error = ValueError("broken handler")

    def failing(obj):
        raise caught_error

    with pytest.raises(SerializationError) as caught:
        encode_with_handler(failing, 5, ("items", 2), _fake_context()[0])

    assert caught.value.error_name == "SERIALIZE_HANDLER_FAILED"
    assert caught.value.label == "$.items[2]"
    assert caught.value.__cause__ is caught_error


@pytest.mark.parametrize(
    "library_error",
    [SerializationError(message="already a card"), DeserializationError(message="also a card")],
    ids=["SerializationError", "DeserializationError"],
)
def test_a_library_error_passes_through_unchanged(library_error):
    def failing(obj):
        raise library_error

    with pytest.raises(type(library_error)) as caught:
        encode_with_handler(failing, 5, (), _fake_context()[0])

    assert caught.value is library_error


def test_a_recursion_error_passes_through_unchanged():
    overflow = RecursionError("too deep")

    def failing(obj):
        raise overflow

    with pytest.raises(RecursionError) as caught:
        encode_with_handler(failing, 5, (), _fake_context()[0])

    assert caught.value is overflow
