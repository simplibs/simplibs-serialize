from collections import namedtuple
from typing import NamedTuple

import pytest

from simplibs.serialize.logic._common_helpers import is_named_tuple_class


class TypedPoint(NamedTuple):
    x: int
    y: int


CollectionsPoint = namedtuple("CollectionsPoint", ["x", "y"])


class PlainTupleChild(tuple):
    """A tuple subclass without fields."""


class FakeNamedTuple(tuple):
    """Has `_fields` but not `_asdict`, so it is not the real thing."""

    _fields = ("x",)


@pytest.mark.parametrize("cls", [TypedPoint, CollectionsPoint], ids=["NamedTuple", "namedtuple"])
def test_true_for_named_tuple_classes(cls):
    assert is_named_tuple_class(cls) is True


@pytest.mark.parametrize(
    "cls",
    [tuple, PlainTupleChild, FakeNamedTuple, list, int],
    ids=["tuple", "tuple_subclass", "fake", "list", "int"],
)
def test_false_for_other_classes(cls):
    assert is_named_tuple_class(cls) is False


@pytest.mark.parametrize(
    "obj",
    [TypedPoint(1, 2), CollectionsPoint(1, 2), (1, 2), None, 5, "text"],
    ids=["NamedTuple_instance", "namedtuple_instance", "tuple_instance", "none", "int", "text"],
)
def test_false_for_anything_that_is_not_a_class(obj):
    assert is_named_tuple_class(obj) is False
