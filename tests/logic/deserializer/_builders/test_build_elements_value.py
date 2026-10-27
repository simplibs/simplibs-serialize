from collections import deque
from collections.abc import Collection, Iterable, MutableSequence, MutableSet, Sequence, Set
from datetime import date
from typing import Any

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_elements_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


def _real_context() -> DeserializeContext:
    return DeserializeContext(strict=True, build_value=build_value)


def _fake_context():
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_build_value(data, annotation, location, context):
        calls.append((data, annotation, location))
        return data

    return DeserializeContext(strict=True, build_value=fake_build_value), calls


def _build(data, annotation, location=()):
    return build_elements_value(data, annotation, location, _real_context())


# ---------- every container ----------

@pytest.mark.parametrize(
    "annotation, expected, kind",
    [
        pytest.param(list[int], [1, 2, 2], list, id="list"),
        pytest.param(set[int], {1, 2}, set, id="set"),
        pytest.param(frozenset[int], frozenset({1, 2}), frozenset, id="frozenset"),
        pytest.param(deque[int], deque([1, 2, 2]), deque, id="deque"),
        pytest.param(Sequence[int], [1, 2, 2], list, id="Sequence"),
        pytest.param(MutableSequence[int], [1, 2, 2], list, id="MutableSequence"),
        pytest.param(Collection[int], [1, 2, 2], list, id="Collection"),
        pytest.param(Iterable[int], [1, 2, 2], list, id="Iterable"),
        pytest.param(Set[int], frozenset({1, 2}), frozenset, id="abstract_Set"),
        pytest.param(MutableSet[int], {1, 2}, set, id="MutableSet"),
    ],
)
def test_the_container_the_annotation_asks_for(annotation, expected, kind):
    result = _build([1, 2, 2], annotation)

    assert result == expected
    assert type(result) is kind


@pytest.mark.parametrize(
    "annotation, data, expected",
    [
        pytest.param(list, [1, "a", None], [1, "a", None], id="list"),
        pytest.param(set, [1, "a"], {1, "a"}, id="set"),
        pytest.param(deque, [1, "a", None], deque([1, "a", None]), id="deque"),
    ],
)
def test_a_bare_container_takes_items_of_any_kind(annotation, data, expected):
    result = _build(data, annotation)

    assert result == expected
    assert type(result) is annotation


def test_a_tuple_of_data_is_accepted_as_a_list():
    assert _build((1, 2), list[int]) == [1, 2]


def test_an_empty_list_gives_an_empty_container():
    assert _build([], list[int]) == []
    assert _build([], set[int]) == set()


def test_items_are_built_against_the_item_annotation():
    assert _build(["2026-01-02"], list[date]) == [date(2026, 1, 2)]


def test_a_duplicate_in_a_set_is_not_refused():
    assert _build([1, 1], set[int]) == {1}


# ---------- data that is no list ----------

@pytest.mark.parametrize(
    "data",
    ["abc", {"a": 1}, 5, None, True],
    ids=["text", "object", "int", "none", "bool"],
)
def test_data_that_is_not_a_list_is_a_wrong_type_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, list[int], ("items",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.items"
    assert caught.value.value == data


# ---------- locations ----------

def test_every_item_is_built_below_its_index():
    context, calls = _fake_context()

    build_elements_value([10, 20], list[int], ("rows", 0), context)

    assert calls == [(10, int, ("rows", 0, 0)), (20, int, ("rows", 0, 1))]


def test_a_bare_container_builds_its_items_as_any():
    context, calls = _fake_context()

    build_elements_value([1], list, (), context)

    assert calls == [(1, Any, (0,))]


def test_an_item_that_does_not_fit_is_located_by_its_index():
    with pytest.raises(DeserializationError) as caught:
        _build([1, "x"], list[int], ("a",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.a[1]"


# ---------- a set that cannot hold its items ----------

def test_an_unhashable_item_for_a_set_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        _build([[1]], set, ("tags",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.tags"
    assert isinstance(caught.value.__cause__, TypeError)
