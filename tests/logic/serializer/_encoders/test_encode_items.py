from collections import deque
from enum import Enum

import pytest

from simplibs.serialize.logic.serializer._classes import SerializeContext
from simplibs.serialize.logic.serializer._encoders import encode_items


class Color(Enum):
    RED = "red"
    BLUE = "blue"


def _context(convert=lambda obj: obj):
    """A context whose dispatcher only records the calls and applies `convert`."""
    calls = []

    def fake_encode_value(obj, location, context):
        calls.append((obj, location))
        return convert(obj)

    return SerializeContext(default=None, allow_nan=False, encode_value=fake_encode_value), calls


@pytest.mark.parametrize(
    "obj, expected",
    [
        pytest.param([3, 1, 2], [3, 1, 2], id="list"),
        pytest.param((3, 1, 2), [3, 1, 2], id="tuple"),
        pytest.param(deque([3, 1, 2]), [3, 1, 2], id="deque"),
        pytest.param(range(3, 0, -1), [3, 2, 1], id="range"),
    ],
)
def test_a_sequence_keeps_its_order(obj, expected):
    context, _ = _context()

    assert encode_items(obj, (), context) == expected


def test_the_result_is_a_list():
    context, _ = _context()

    assert type(encode_items((1, 2), (), context)) is list


@pytest.mark.parametrize("obj", [{3, 1, 2}, frozenset({3, 1, 2})], ids=["set", "frozenset"])
def test_a_set_is_sorted(obj):
    context, _ = _context()

    assert encode_items(obj, (), context) == [1, 2, 3]


def test_the_keys_of_a_dict_are_sorted_and_its_values_keep_their_order():
    context, _ = _context()
    data = {"b": 1, "a": 2}

    assert encode_items(data.keys(), (), context) == ["a", "b"]
    assert encode_items(data.values(), (), context) == [1, 2]


def test_a_set_is_sorted_after_conversion():
    """A set of enum members is ordered by what is written for each, not by the members."""
    context, _ = _context(convert=lambda member: member.value)

    assert encode_items({Color.RED, Color.BLUE}, (), context) == ["blue", "red"]


def test_an_empty_set_and_an_empty_list_give_an_empty_list():
    context, _ = _context()

    assert encode_items(set(), (), context) == []
    assert encode_items([], (), context) == []


def test_every_item_is_converted_below_its_index():
    context, calls = _context(convert=lambda item: item * 10)

    result = encode_items([1, 2, 3], ("data",), context)

    assert result == [10, 20, 30]
    assert calls == [(1, ("data", 0)), (2, ("data", 1)), (3, ("data", 2))]


def test_the_indexes_of_a_set_are_positions_in_its_own_order():
    context, calls = _context()

    encode_items({"x", "y", "z"}, (), context)

    assert sorted(location for _, location in calls) == [(0,), (1,), (2,)]
