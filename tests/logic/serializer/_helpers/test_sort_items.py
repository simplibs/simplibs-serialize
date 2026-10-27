from itertools import permutations

import pytest

from simplibs.serialize.logic.serializer._helpers import sort_items


@pytest.mark.parametrize(
    "items, expected",
    [
        pytest.param([10, 2, 33, 1], [1, 2, 10, 33], id="numbers_by_size"),
        pytest.param([2, 1.5, 3], [1.5, 2, 3], id="int_and_float"),
        pytest.param(["b", "a", "c"], ["a", "b", "c"], id="text"),
        pytest.param([[2], [1]], [[1], [2]], id="comparable_lists"),
        pytest.param([], [], id="empty"),
        pytest.param([None, 1], [1, None], id="number_and_none_by_json_text"),
        pytest.param([{"b": 1}, {"a": 2}], [{"a": 2}, {"b": 1}], id="dicts_by_json_text"),
        pytest.param([[1], ["a"]], [["a"], [1]], id="uncomparable_lists_by_json_text"),
    ],
)
def test_sort_items(items, expected):
    assert sort_items(items) == expected


def test_returns_a_new_list_and_leaves_the_input_alone():
    items = [3, 1, 2]

    result = sort_items(items)

    assert result is not items
    assert items == [3, 1, 2]


def test_the_same_items_in_any_order_give_the_same_list():
    mixed = [None, 1, "a", {"k": 1}]

    results = {repr(sort_items(list(order))) for order in permutations(mixed)}

    assert len(results) == 1
