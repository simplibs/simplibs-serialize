import importlib
from dataclasses import dataclass
from typing import Annotated, NamedTuple, TypedDict

import pytest

from simplibs.serialize import register_type
from simplibs.serialize.logic.deserializer._builders import (
    build_annotated_value,
    build_dataclass_value,
    build_elements_value,
    build_named_tuple_value,
    build_primitive_value,
    build_typed_dict_value,
    build_value,
)
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


# A `RecursionError` never means "this value cannot be built": it means the data is nested
# deeper than the interpreter allows, and it is turned into one card at the top, in `deserialize`.
# Every builder that catches `Exception` has to let it through, so that the card does not depend
# on the place where the limit happened to be reached.

_OVERFLOW = RecursionError("maximum recursion depth exceeded")


def overflow():
    """Called from an annotation written as text: resolving that annotation raises the error."""
    raise _OVERFLOW


@dataclass
class OverflowingDataclass:
    a: "overflow()"  # noqa: F821


class OverflowingNamedTuple(NamedTuple):
    a: "overflow()"  # noqa: F821


class OverflowingTypedDict(TypedDict):
    a: "overflow()"  # noqa: F821


class Overflowing(int):
    """An int subclass whose constructor hits the limit."""

    def __new__(cls, value):
        raise _OVERFLOW


class Hashy:
    """An item that hits the limit when a set asks for its hash."""

    def __hash__(self) -> int:
        raise _OVERFLOW


def _context() -> DeserializeContext:
    return DeserializeContext(strict=True, build_value=build_value)


def _check_rule(value) -> bool:
    """A predicate, so that `Annotated` has a rule to run."""
    return True


def _raising_validate(value, rule, **options):
    raise _OVERFLOW


@pytest.fixture
def overflowing_validate(monkeypatch):
    """Make the call that runs an `Annotated` rule hit the limit."""
    # The package exports the function under the same name as its module, so the module is looked up by path
    module = importlib.import_module("simplibs.serialize.logic.deserializer._builders.build_annotated_value")
    monkeypatch.setattr(module, "validate", _raising_validate)


def test_the_type_hints_of_a_dataclass_may_hit_the_limit():
    with pytest.raises(RecursionError) as caught:
        build_dataclass_value({"a": 1}, OverflowingDataclass, (), _context())

    assert caught.value is _OVERFLOW


def test_the_type_hints_of_a_named_tuple_may_hit_the_limit():
    with pytest.raises(RecursionError) as caught:
        build_named_tuple_value({"a": 1}, OverflowingNamedTuple, (), _context())

    assert caught.value is _OVERFLOW


def test_the_type_hints_of_a_typed_dict_may_hit_the_limit():
    with pytest.raises(RecursionError) as caught:
        build_typed_dict_value({"a": 1}, OverflowingTypedDict, (), _context())

    assert caught.value is _OVERFLOW


def test_the_constructor_of_a_primitive_subclass_may_hit_the_limit():
    with pytest.raises(RecursionError) as caught:
        build_primitive_value(1, Overflowing, ())

    assert caught.value is _OVERFLOW


def test_the_hash_of_an_item_may_hit_the_limit_when_a_set_is_made():
    register_type(Hashy, from_func=lambda data, annotation: Hashy())

    with pytest.raises(RecursionError) as caught:
        build_elements_value([1], set[Hashy], (), _context())

    assert caught.value is _OVERFLOW


def test_a_rule_of_annotated_may_hit_the_limit(overflowing_validate):
    with pytest.raises(RecursionError) as caught:
        build_annotated_value(5, Annotated[int, _check_rule], (), _context())

    assert caught.value is _OVERFLOW
