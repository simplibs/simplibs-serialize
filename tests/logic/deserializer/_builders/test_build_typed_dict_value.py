from datetime import date
from typing import NotRequired, Required, TypedDict

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_typed_dict_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


class Person(TypedDict):
    name: str
    age: int


class Options(TypedDict, total=False):
    verbose: bool
    level: int


class Mixed(TypedDict):
    name: str
    note: NotRequired[int]


class Forced(TypedDict, total=False):
    name: Required[str]
    note: int


class Base(TypedDict):
    id: int


class Derived(Base):
    label: str


class Event(TypedDict):
    when: date
    person: Person


class Unresolvable(TypedDict):
    a: "DoesNotExist"  # noqa: F821


def _real_context(strict=True) -> DeserializeContext:
    return DeserializeContext(strict=strict, build_value=build_value)


def _build(data, annotation, location=(), strict=True):
    return build_typed_dict_value(data, annotation, location, _real_context(strict))


# ---------- required and optional keys ----------

def test_a_typed_dict_with_all_keys():
    result = _build({"name": "ann", "age": 5}, Person)

    assert result == {"name": "ann", "age": 5}
    assert type(result) is dict


def test_total_false_makes_every_key_optional():
    assert _build({}, Options) == {}
    assert _build({"level": 3}, Options) == {"level": 3}


def test_not_required_makes_one_key_optional():
    assert _build({"name": "ann"}, Mixed) == {"name": "ann"}
    assert _build({"name": "ann", "note": 1}, Mixed) == {"name": "ann", "note": 1}


def test_required_makes_one_key_required_in_a_total_false_dict():
    assert _build({"name": "ann"}, Forced) == {"name": "ann"}
    with pytest.raises(DeserializationError) as caught:
        _build({"note": 1}, Forced)

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.value == ["name"]


def test_the_result_has_only_the_keys_that_were_present():
    assert _build({"verbose": True}, Options) == {"verbose": True}


def test_keys_of_a_parent_typed_dict_are_required_too():
    assert _build({"id": 1, "label": "x"}, Derived) == {"id": 1, "label": "x"}
    with pytest.raises(DeserializationError) as caught:
        _build({"label": "x"}, Derived)

    assert caught.value.value == ["id"]


# ---------- missing and unknown ----------

def test_missing_keys_are_reported_sorted():
    with pytest.raises(DeserializationError) as caught:
        _build({}, Person, ("row",))

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.label == "$.row"
    assert caught.value.value == ["age", "name"]


def test_an_unknown_key_is_an_error_when_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"name": "ann", "age": 5, "extra": 1}, Person)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert caught.value.value == ["extra"]


def test_an_unknown_key_is_ignored_and_left_out_when_not_strict():
    assert _build({"name": "ann", "age": 5, "extra": 1}, Person, strict=False) == {"name": "ann", "age": 5}


def test_a_typo_is_reported_as_unknown_with_what_is_missing():
    with pytest.raises(DeserializationError) as caught:
        _build({"name": "ann", "agee": 5}, Person)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert "Required but absent: 'age'" in str(caught.value.problem)


def test_a_typo_is_a_missing_field_when_not_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"name": "ann", "agee": 5}, Person, strict=False)

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.value == ["age"]


# ---------- data that is no object ----------

@pytest.mark.parametrize("data", [[1], "abc", 5, None], ids=["list", "text", "int", "none"])
def test_data_that_is_not_an_object_is_a_wrong_type_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, Person, ("row",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.row"
    assert caught.value.value == data


# ---------- values ----------

def test_values_are_built_against_their_own_annotations():
    result = _build({"when": "2026-01-02", "person": {"name": "ann", "age": 5}}, Event)

    assert result == {"when": date(2026, 1, 2), "person": {"name": "ann", "age": 5}}


def test_a_value_that_does_not_fit_is_located_by_its_key():
    with pytest.raises(DeserializationError) as caught:
        _build({"name": "ann", "age": "old"}, Person, ("people", 0))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.people[0].age"


def test_a_nested_typed_dict_has_the_full_location():
    with pytest.raises(DeserializationError) as caught:
        _build({"when": "2026-01-02", "person": {"name": "ann", "age": "old"}}, Event)

    assert caught.value.label == "$.person.age"


def test_a_not_required_value_that_does_not_fit_is_located_by_its_key():
    with pytest.raises(DeserializationError) as caught:
        _build({"name": "ann", "note": "x"}, Mixed)

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.note"


# ---------- annotations that cannot be resolved ----------

def test_an_unresolvable_annotation_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1}, Unresolvable, ("row",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.row"
    assert isinstance(caught.value.__cause__, NameError)
