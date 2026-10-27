from collections import namedtuple
from typing import NamedTuple

import pytest

from simplibs.serialize.logic._common_helpers import is_named_tuple


class TypedPoint(NamedTuple):
    x: int
    y: int


CollectionsPoint = namedtuple("CollectionsPoint", ["x", "y"])


class PlainTupleChild(tuple):
    """A tuple subclass without fields."""


@pytest.mark.parametrize(
    "obj",
    [TypedPoint(1, 2), CollectionsPoint(1, 2)],
    ids=["NamedTuple", "namedtuple"],
)
def test_true_for_named_tuple_instances(obj):
    assert is_named_tuple(obj) is True


@pytest.mark.parametrize(
    "obj",
    [(1, 2), PlainTupleChild((1, 2)), [1, 2], None, 5],
    ids=["tuple", "tuple_subclass", "list", "none", "int"],
)
def test_false_for_everything_else(obj):
    assert is_named_tuple(obj) is False


@pytest.mark.parametrize("cls", [TypedPoint, CollectionsPoint], ids=["NamedTuple", "namedtuple"])
def test_false_for_the_class_itself(cls):
    """A class given by mistake is not an instance."""
    assert is_named_tuple(cls) is False
