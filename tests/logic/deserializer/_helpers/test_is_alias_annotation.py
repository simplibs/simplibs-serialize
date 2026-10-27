import typing
from typing import NewType, TypeVar

import pytest

from simplibs.serialize.logic.deserializer._helpers import is_alias_annotation


UserId = NewType("UserId", int)
AdminId = NewType("AdminId", UserId)
T = TypeVar("T")
TypeAliasType = getattr(typing, "TypeAliasType", None)


def test_true_for_a_newtype():
    assert is_alias_annotation(UserId) is True


def test_true_for_a_newtype_of_a_newtype():
    assert is_alias_annotation(AdminId) is True


def test_true_for_a_type_variable():
    assert is_alias_annotation(T) is True


@pytest.mark.skipif(TypeAliasType is None, reason="`type` aliases exist from Python 3.12")
def test_true_for_a_type_alias():
    alias = TypeAliasType("Ids", list[int])

    assert is_alias_annotation(alias) is True


@pytest.mark.parametrize(
    "annotation",
    [int, list[int], int | None, typing.Any, None, "UserId", 5],
    ids=["class", "subscripted", "union", "any", "none", "text", "number"],
)
def test_false_for_everything_else(annotation):
    assert is_alias_annotation(annotation) is False
