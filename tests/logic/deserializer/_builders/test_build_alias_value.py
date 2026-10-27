import typing
from typing import Any, NewType, TypeVar

import pytest

from simplibs.serialize import DeserializationError, register_type
from simplibs.serialize.logic.deserializer._builders import build_alias_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


UserId = NewType("UserId", int)
AdminId = NewType("AdminId", UserId)
Unbound = TypeVar("Unbound")
Bounded = TypeVar("Bounded", bound=int)
TypeAliasType = getattr(typing, "TypeAliasType", None)


def _real_context() -> DeserializeContext:
    return DeserializeContext(strict=True, build_value=build_value)


def _fake_context():
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_build_value(data, annotation, location, context):
        calls.append((data, annotation, location))
        return data

    return DeserializeContext(strict=True, build_value=fake_build_value), calls


# ---------- which annotation is built ----------

def test_a_newtype_is_built_as_what_it_wraps():
    context, calls = _fake_context()

    build_alias_value(5, UserId, ("ids", 0), context)

    assert calls == [(5, int, ("ids", 0))]


def test_a_newtype_of_a_newtype_goes_one_step_at_a_time():
    context, calls = _fake_context()

    build_alias_value(5, AdminId, (), context)

    assert calls == [(5, UserId, ())]


@pytest.mark.skipif(TypeAliasType is None, reason="`type` aliases exist from Python 3.12")
def test_a_type_alias_is_built_as_its_value():
    context, calls = _fake_context()

    build_alias_value([1], TypeAliasType("Ids", list[int]), (), context)

    assert calls == [([1], list[int], ())]


def test_an_unbound_type_variable_is_built_as_any():
    context, calls = _fake_context()

    build_alias_value("anything", Unbound, (), context)

    assert calls == [("anything", Any, ())]


def test_a_bound_type_variable_is_built_as_its_bound():
    context, calls = _fake_context()

    build_alias_value(5, Bounded, (), context)

    assert calls == [(5, int, ())]


# ---------- with the real dispatcher ----------

def test_a_newtype_gives_the_value_of_its_type():
    assert build_alias_value(5, UserId, (), _real_context()) == 5


def test_a_newtype_of_a_newtype_gives_the_value_of_the_innermost_type():
    assert build_alias_value(5, AdminId, (), _real_context()) == 5


def test_a_newtype_checks_the_data_like_its_type_does():
    with pytest.raises(DeserializationError) as caught:
        build_alias_value("x", UserId, ("user",), _real_context())

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.user"


@pytest.mark.skipif(TypeAliasType is None, reason="`type` aliases exist from Python 3.12")
def test_a_type_alias_checks_the_data_like_its_value_does():
    alias = TypeAliasType("Ids", list[int])

    assert build_alias_value([1, 2], alias, (), _real_context()) == [1, 2]
    with pytest.raises(DeserializationError):
        build_alias_value(["x"], alias, (), _real_context())


def test_an_unbound_type_variable_lets_anything_through():
    assert build_alias_value({"a": [1]}, Unbound, (), _real_context()) == {"a": [1]}


def test_a_bound_type_variable_checks_against_its_bound():
    assert build_alias_value(5, Bounded, (), _real_context()) == 5
    with pytest.raises(DeserializationError):
        build_alias_value("x", Bounded, (), _real_context())


def test_a_handler_registered_for_a_newtype_is_found_before_the_alias_builder():
    register_type(UserId, from_func=lambda data, annotation: ("custom", data))

    assert build_value(5, UserId, (), _real_context()) == ("custom", 5)
