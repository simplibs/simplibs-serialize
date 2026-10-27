import math

import pytest

from simplibs.serialize.logic.deserializer._helpers import key_candidates


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("abc", ["abc"], id="plain_text"),
        pytest.param("", [""], id="empty_text"),
        pytest.param("12", ["12", 12], id="whole_number"),
        pytest.param("0", ["0", 0], id="zero"),
        pytest.param("-3", ["-3", -3], id="negative_number"),
        pytest.param("1.5", ["1.5", 1.5], id="decimal_number"),
        pytest.param("1e5", ["1e5", 100000.0], id="exponent"),
        pytest.param("true", ["true", True], id="true"),
        pytest.param("false", ["false", False], id="false"),
        pytest.param("null", ["null", None], id="null"),
        # Not the canonical way to write a whole number: never an int, only a float reading
        pytest.param("012", ["012", 12.0], id="leading_zero_is_no_int"),
        pytest.param("+1", ["+1", 1.0], id="plus_sign_is_no_int"),
        # Underscores and spaces are accepted by Python, not by JSON
        pytest.param("1_0", ["1_0"], id="underscore"),
        pytest.param(" 1", [" 1"], id="leading_space"),
        pytest.param("1 ", ["1 "], id="trailing_space"),
        pytest.param("True", ["True"], id="python_true_is_just_text"),
        pytest.param("None", ["None"], id="python_none_is_just_text"),
    ],
)
def test_key_candidates(text, expected):
    result = key_candidates(text)

    assert result == expected
    assert [type(item) for item in result] == [type(item) for item in expected]


def test_nan_is_a_float_candidate():
    text, number = key_candidates("nan")

    assert text == "nan"
    assert math.isnan(number)


@pytest.mark.parametrize("text, expected", [("inf", math.inf), ("-inf", -math.inf)])
def test_infinity_is_a_float_candidate(text, expected):
    assert key_candidates(text) == [text, expected]


def test_the_text_itself_always_comes_first():
    for text in ["abc", "12", "1.5", "true", "null", "nan", ""]:
        assert key_candidates(text)[0] == text
