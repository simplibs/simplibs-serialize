from datetime import date
from enum import Enum

import pytest

from simplibs.serialize import DeserializationError, SerializationError
from simplibs.serialize.logic.deserializer._builders import build_with_handler
from simplibs.serialize.logic.registry._handlers.builtin import BUILTIN_FROM_HANDLERS


class Color(Enum):
    RED = "red"


def test_the_handler_gets_the_data_and_the_annotation_and_its_result_is_returned():
    calls = []

    def handler(data, annotation):
        calls.append((data, annotation))
        return "built"

    result = build_with_handler(handler, {"a": 1}, date, ("when",))

    assert result == "built"
    assert calls == [({"a": 1}, date)]


def test_a_builtin_handler_builds_its_value():
    assert build_with_handler(BUILTIN_FROM_HANDLERS[date], "2026-01-02", date, ()) == date(2026, 1, 2)


def test_a_number_where_a_date_belongs_is_one_card_with_a_location():
    with pytest.raises(DeserializationError) as caught:
        build_with_handler(BUILTIN_FROM_HANDLERS[date], 5, date, ("when",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.when"
    assert isinstance(caught.value.__cause__, TypeError)


def test_an_enum_value_that_does_not_exist_is_a_card_with_the_cause_kept():
    with pytest.raises(DeserializationError) as caught:
        build_with_handler(BUILTIN_FROM_HANDLERS[Enum], "blue", Color, ("color",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.color"
    assert isinstance(caught.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "failure",
    [KeyError("missing"), AttributeError("no attribute"), ZeroDivisionError("division by zero")],
    ids=["KeyError", "AttributeError", "ZeroDivisionError"],
)
def test_any_ordinary_error_of_the_handler_is_wrapped(failure):
    def failing(data, annotation):
        raise failure

    with pytest.raises(DeserializationError) as caught:
        build_with_handler(failing, 1, date, ())

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.__cause__ is failure


@pytest.mark.parametrize(
    "library_error",
    [DeserializationError(message="already a card"), SerializationError(message="also a card")],
    ids=["DeserializationError", "SerializationError"],
)
def test_a_library_error_passes_through_unchanged(library_error):
    def failing(data, annotation):
        raise library_error

    with pytest.raises(type(library_error)) as caught:
        build_with_handler(failing, 1, date, ())

    assert caught.value is library_error


def test_a_recursion_error_passes_through_unchanged():
    overflow = RecursionError("too deep")

    def failing(data, annotation):
        raise overflow

    with pytest.raises(RecursionError) as caught:
        build_with_handler(failing, 1, date, ())

    assert caught.value is overflow
