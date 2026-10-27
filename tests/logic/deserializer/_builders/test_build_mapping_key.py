import uuid
from datetime import date
from enum import Enum, IntEnum
from typing import Annotated, Any

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_mapping_key, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


class Color(Enum):
    RED = "red"


class Level(IntEnum):
    LOW = 1


def _context() -> DeserializeContext:
    return DeserializeContext(strict=True, build_value=build_value)


def _build(key, annotation, location=()):
    return build_mapping_key(key, annotation, location, _context())


# ---------- the text the annotation asks for ----------

@pytest.mark.parametrize("annotation", [str, Any, object], ids=["str", "Any", "object"])
@pytest.mark.parametrize("key", ["abc", "1", "true", "null", ""], ids=["text", "digits", "true", "null", "empty"])
def test_text_for_text_stays_as_it_is(annotation, key):
    result = _build(key, annotation)

    assert result == key
    assert type(result) is str


# ---------- the forms a text can stand for ----------

@pytest.mark.parametrize(
    "key, annotation, expected",
    [
        pytest.param("12", int, 12, id="int"),
        pytest.param("-3", int, -3, id="negative_int"),
        pytest.param("1.5", float, 1.5, id="float"),
        pytest.param("1", float, 1.0, id="whole_float"),
        pytest.param("true", bool, True, id="true"),
        pytest.param("false", bool, False, id="false"),
        pytest.param("null", type(None), None, id="none"),
        pytest.param("2026-01-02", date, date(2026, 1, 2), id="date"),
        pytest.param(
            "00000000-0000-0000-0000-000000000001", uuid.UUID, uuid.UUID(int=1), id="uuid"
        ),
        pytest.param("red", Color, Color.RED, id="text_enum"),
        pytest.param("1", Level, Level.LOW, id="int_enum_from_digits"),
    ],
)
def test_a_key_is_read_back_as_the_type_of_the_annotation(key, annotation, expected):
    result = _build(key, annotation)

    assert result == expected
    assert type(result) is type(expected)


def test_a_number_never_accepts_the_text_itself_so_a_float_text_is_no_int():
    with pytest.raises(DeserializationError) as caught:
        _build("1.5", int, ("table",))

    assert caught.value.error_name == "DESERIALIZE_INVALID_KEY"
    assert caught.value.label == "$.table"


@pytest.mark.parametrize(
    "key, annotation",
    [
        pytest.param("abc", int, id="text_for_int"),
        pytest.param("", int, id="empty_for_int"),
        pytest.param("abc", float, id="text_for_float"),
        pytest.param("1", bool, id="one_for_bool"),
        pytest.param("yes", bool, id="yes_for_bool"),
        pytest.param("none", type(None), id="wrong_word_for_none"),
        pytest.param("not a date", date, id="text_for_date"),
        pytest.param("blue", Color, id="value_the_enum_does_not_have"),
        pytest.param("2", Level, id="int_the_enum_does_not_have"),
    ],
)
def test_a_key_no_form_fits_is_an_invalid_key_card(key, annotation):
    with pytest.raises(DeserializationError) as caught:
        _build(key, annotation, ("table",))

    assert caught.value.error_name == "DESERIALIZE_INVALID_KEY"
    assert caught.value.label == "$.table"
    assert caught.value.value == key


# ---------- rules and unions decide for themselves ----------

def test_an_annotated_rule_on_a_key_is_checked():
    positive = Annotated[int, lambda value: value > 0]

    assert _build("5", positive) == 5
    with pytest.raises(DeserializationError) as caught:
        _build("-5", positive)
    assert caught.value.error_name == "DESERIALIZE_INVALID_KEY"


def test_a_union_takes_the_first_form_that_fits_which_is_the_text():
    assert _build("1", int | str) == "1"
    assert _build("abc", int | str) == "abc"


def test_an_optional_key_reads_null_as_none_and_digits_as_a_number():
    assert _build("null", int | None) is None
    assert _build("5", int | None) == 5


# ---------- a key that is not text ----------

def test_a_key_that_came_from_python_data_is_built_like_any_value():
    assert _build(5, int) == 5


def test_a_key_that_came_from_python_data_must_fit_the_annotation():
    with pytest.raises(DeserializationError) as caught:
        _build(5, str, ("table",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.table"
