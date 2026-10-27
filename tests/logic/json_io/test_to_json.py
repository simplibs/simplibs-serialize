import json
from dataclasses import dataclass
from datetime import date

import pytest

from simplibs.serialize import SerializationError, serialize, to_json


@dataclass
class Point:
    x: int
    y: int


class Unknown:
    """Nothing knows this class."""


def test_a_dataclass_becomes_indented_text_by_default():
    assert to_json(Point(1, 2)) == '{\n  "x": 1,\n  "y": 2\n}'


def test_the_result_is_text_without_a_trailing_newline():
    result = to_json({"a": 1})

    assert isinstance(result, str)
    assert not result.endswith("\n")


@pytest.mark.parametrize(
    "indent, expected",
    [
        pytest.param(None, '{"a": [1, 2]}', id="compact"),
        pytest.param(4, '{\n    "a": [\n        1,\n        2\n    ]\n}', id="four_spaces"),
        pytest.param("\t", '{\n\t"a": [\n\t\t1,\n\t\t2\n\t]\n}', id="tab"),
    ],
)
def test_indent_as_a_number_a_string_and_none(indent, expected):
    assert to_json({"a": [1, 2]}, indent=indent) == expected


def test_non_ascii_text_is_written_as_it_is_by_default():
    assert to_json("č", indent=None) == '"č"'


def test_ensure_ascii_escapes_it():
    assert to_json("č", indent=None, ensure_ascii=True) == '"\\u010d"'


def test_keys_keep_their_order_by_default_and_are_sorted_on_request():
    data = {"b": 1, "a": 2}

    assert to_json(data, indent=None) == '{"b": 1, "a": 2}'
    assert to_json(data, indent=None, sort_keys=True) == '{"a": 2, "b": 1}'


def test_sort_keys_works_with_keys_of_mixed_types_in_the_original_dict():
    """After `serialize` every key is text, so sorting cannot fail."""
    assert to_json({2: "a", "b": 1, 1: "c"}, indent=None, sort_keys=True) == '{"1": "c", "2": "a", "b": 1}'


@pytest.mark.parametrize("number", [float("nan"), float("inf"), float("-inf")], ids=["nan", "inf", "minus_inf"])
def test_a_non_finite_number_is_an_error_by_default(number):
    with pytest.raises(SerializationError) as caught:
        to_json([number])

    assert caught.value.error_name == "SERIALIZE_NON_FINITE_NUMBER"
    assert caught.value.label == "$[0]"


@pytest.mark.parametrize(
    "number, text",
    [(float("nan"), "NaN"), (float("inf"), "Infinity"), (float("-inf"), "-Infinity")],
    ids=["nan", "inf", "minus_inf"],
)
def test_a_non_finite_number_is_written_when_allowed(number, text):
    assert to_json(number, allow_nan=True) == text


def test_default_deals_with_a_type_nothing_else_knows():
    assert to_json({"a": Unknown()}, indent=None, default=lambda obj: "unknown") == '{"a": "unknown"}'


def test_an_unsupported_value_is_an_error_with_its_location():
    with pytest.raises(SerializationError) as caught:
        to_json({"items": [1, Unknown()]})

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_TYPE"
    assert caught.value.label == "$.items[1]"


def test_the_text_is_what_serialize_makes_of_the_object():
    obj = {"when": date(2026, 1, 2), "tags": {"b", "a"}, "point": Point(1, 2)}

    assert json.loads(to_json(obj)) == serialize(obj)
