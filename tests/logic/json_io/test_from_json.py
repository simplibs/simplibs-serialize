import math
from dataclasses import dataclass
from datetime import date

import pytest

from simplibs.serialize import DeserializationError, from_json


@dataclass
class Point:
    x: int
    y: int


# ---------- valid text ----------

def test_text_becomes_a_dataclass():
    assert from_json('{"x": 1, "y": 2}', Point) == Point(1, 2)


@pytest.mark.parametrize(
    "text, annotation, expected",
    [
        pytest.param("[1, 2]", list[int], [1, 2], id="list"),
        pytest.param('{"a": 1}', dict[str, int], {"a": 1}, id="dict"),
        pytest.param('["2026-01-02"]', list[date], [date(2026, 1, 2)], id="dates"),
        pytest.param("5", int, 5, id="top_level_number"),
        pytest.param('"abc"', str, "abc", id="top_level_text"),
        pytest.param("null", int | None, None, id="null"),
        pytest.param('[{"x": 1, "y": 2}]', list[Point], [Point(1, 2)], id="list_of_dataclasses"),
    ],
)
def test_text_becomes_what_the_annotation_asks_for(text, annotation, expected):
    assert from_json(text, annotation) == expected


def test_utf8_bytes_are_accepted():
    assert from_json('{"x": 1, "y": 2}'.encode("utf-8"), Point) == Point(1, 2)


def test_non_ascii_text_survives():
    assert from_json('"č"', str) == "č"


# ---------- a byte order mark ----------

def test_a_bom_in_front_of_text_is_not_part_of_the_json():
    assert from_json("\ufeff[1, 2]", list[int]) == [1, 2]


def test_a_bom_in_front_of_bytes_is_not_part_of_the_json():
    assert from_json(b"\xef\xbb\xbf[1, 2]", list[int]) == [1, 2]


# ---------- text that is no JSON ----------

@pytest.mark.parametrize(
    "text",
    ['{"x": 1,}', "{'x': 1}", "", "   ", "[1, 2", "not json"],
    ids=["trailing_comma", "single_quotes", "empty", "blank", "unclosed", "plain_words"],
)
def test_invalid_text_is_an_invalid_json_card(text):
    with pytest.raises(DeserializationError) as caught:
        from_json(text, Point)

    assert caught.value.error_name == "DESERIALIZE_INVALID_JSON"
    assert caught.value.label == "json_str"


def test_the_card_names_line_and_column_and_shows_the_text_around_the_mistake():
    with pytest.raises(DeserializationError) as caught:
        from_json('{\n  "x": 1\n  "y": 2\n}', Point)

    assert "line 3, column 3" in str(caught.value.problem)
    assert '"y": 2' in caught.value.value


def test_invalid_bytes_are_an_invalid_json_card():
    with pytest.raises(DeserializationError) as caught:
        from_json(b'"\xff"', str)

    assert caught.value.error_name == "DESERIALIZE_INVALID_JSON"


# Deeper than the recursion limit of every supported Python (3.12+ counts C recursion separately)
_DEPTH = 100_000


def test_text_nested_beyond_the_interpreters_limit_is_the_same_card():
    with pytest.raises(DeserializationError) as caught:
        from_json("[" * _DEPTH + "]" * _DEPTH, list)

    assert caught.value.error_name == "DESERIALIZE_INVALID_JSON"
    assert isinstance(caught.value.__cause__, RecursionError)


# ---------- valid JSON of the wrong shape ----------

def test_json_that_does_not_fit_the_type_is_a_card_with_the_location():
    with pytest.raises(DeserializationError) as caught:
        from_json('{"x": "bad", "y": 2}', Point)

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.x"


def test_an_unknown_key_is_an_error_when_strict():
    with pytest.raises(DeserializationError) as caught:
        from_json('{"x": 1, "y": 2, "z": 3}', Point)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"


def test_an_unknown_key_is_ignored_when_not_strict():
    assert from_json('{"x": 1, "y": 2, "z": 3}', Point, strict=False) == Point(1, 2)


# ---------- nan is read ----------

def test_nan_and_infinity_are_read_as_float_json_accepts_them():
    assert math.isnan(from_json("NaN", float))
    assert from_json("[Infinity, -Infinity]", list[float]) == [math.inf, -math.inf]


def test_an_unsupported_annotation_is_a_card():
    with pytest.raises(DeserializationError) as caught:
        from_json("1", complex)

    assert caught.value.error_name == "DESERIALIZE_UNSUPPORTED_ANNOTATION"
