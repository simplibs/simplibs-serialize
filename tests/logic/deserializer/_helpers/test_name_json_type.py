from collections import OrderedDict
from enum import IntEnum

import pytest

from simplibs.serialize.logic.deserializer._helpers import name_json_type


class Point:
    """A class that is no JSON kind."""


class Level(IntEnum):
    LOW = 1


class Name(str):
    """A str subclass."""


@pytest.mark.parametrize(
    "data, expected",
    [
        pytest.param(None, "null", id="none"),
        pytest.param(True, "a boolean", id="true"),
        pytest.param(False, "a boolean", id="false"),
        pytest.param(5, "an integer", id="int"),
        pytest.param(1.5, "a number", id="float"),
        pytest.param(float("nan"), "a number", id="nan"),
        pytest.param("x", "text", id="text"),
        pytest.param("", "text", id="empty_text"),
        pytest.param([1], "a list", id="list"),
        pytest.param([], "a list", id="empty_list"),
        pytest.param((1, 2), "a list", id="tuple"),
        pytest.param({"a": 1}, "an object", id="dict"),
        pytest.param({}, "an object", id="empty_dict"),
        pytest.param(OrderedDict(a=1), "an object", id="mapping"),
        pytest.param(Level.LOW, "an integer", id="int_subclass"),
        pytest.param(Name("a"), "text", id="str_subclass"),
    ],
)
def test_names_the_json_kind(data, expected):
    assert name_json_type(data) == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        pytest.param({1, 2}, "a set", id="set"),
        pytest.param(b"x", "a bytes", id="bytes"),
        pytest.param(Point(), "a Point", id="custom_class"),
        pytest.param(1 + 2j, "a complex", id="complex"),
    ],
)
def test_anything_that_is_no_json_falls_back_to_its_class_name(data, expected):
    assert name_json_type(data) == expected


def test_a_boolean_is_not_called_an_integer():
    assert name_json_type(True) != name_json_type(1)
