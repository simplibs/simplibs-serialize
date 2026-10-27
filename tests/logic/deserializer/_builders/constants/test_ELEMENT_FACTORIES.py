from collections import abc, deque

import pytest

from simplibs.serialize.logic.deserializer._builders import BUILDER_TABLE, build_elements_value
from simplibs.serialize.logic.deserializer._builders.constants import ELEMENT_FACTORIES


def test_is_read_only():
    with pytest.raises(TypeError):
        ELEMENT_FACTORIES[list] = list


def test_knows_exactly_these_origins():
    assert set(ELEMENT_FACTORIES) == {set, frozenset, deque, abc.Set, abc.MutableSet}


@pytest.mark.parametrize(
    "origin, expected, kind",
    [
        pytest.param(set, {1, 2}, set, id="set"),
        pytest.param(frozenset, frozenset({1, 2}), frozenset, id="frozenset"),
        pytest.param(deque, deque([1, 2, 2]), deque, id="deque"),
        pytest.param(abc.Set, frozenset({1, 2}), frozenset, id="abstract_set_is_frozen"),
        pytest.param(abc.MutableSet, {1, 2}, set, id="mutable_set_is_a_set"),
    ],
)
def test_each_factory_makes_its_container(origin, expected, kind):
    result = ELEMENT_FACTORIES[origin]([1, 2, 2])

    assert result == expected
    assert type(result) is kind


@pytest.mark.parametrize(
    "origin",
    [list, abc.Sequence, abc.MutableSequence, abc.Collection, abc.Iterable, tuple],
    ids=lambda origin: origin.__name__,
)
def test_everything_else_is_left_to_stay_a_list(origin):
    assert origin not in ELEMENT_FACTORIES


def test_every_origin_is_one_the_elements_builder_serves():
    assert all(BUILDER_TABLE[origin] is build_elements_value for origin in ELEMENT_FACTORIES)
