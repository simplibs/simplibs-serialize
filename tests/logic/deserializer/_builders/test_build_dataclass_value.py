from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Annotated, Any, Generic, TypeVar

import pytest

from simplibs.serialize import DeserializationError, serialized_field
from simplibs.serialize.logic.deserializer._builders import build_dataclass_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


T = TypeVar("T")


@dataclass
class Plain:
    a: int
    b: str


@dataclass
class Inner:
    x: int


@dataclass
class Outer:
    inner: Inner
    items: list[Inner]


@dataclass
class Aliased:
    user_name: str = serialized_field(alias="userName")


@dataclass
class WithSecret:
    name: str
    secret: str = serialized_field(exclude=True, default="none")


@dataclass
class Unbuildable:
    secret: str = serialized_field(exclude=True)


@dataclass
class WithDerived:
    a: int
    computed: int = field(init=False, default=7)


@dataclass
class WithDefaults:
    a: int
    b: int = 5
    tags: list = field(default_factory=list)
    note: str | None = None


@dataclass
class Box(Generic[T]):
    item: T
    items: list[T]


@dataclass
class Child:
    value: int


@dataclass
class Parent:
    child: "Child"


@dataclass
class WithRule:
    port: Annotated[int, lambda value: value > 0]


@dataclass(frozen=True, slots=True)
class FrozenSlots:
    a: int


@dataclass
class KeywordOnly:
    a: int = field(kw_only=True)


@dataclass
class Rejecting:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("negative")


_CARD = DeserializationError(message="already a card")


@dataclass
class RaisingCard:
    value: int

    def __post_init__(self):
        raise _CARD


@dataclass
class Unresolvable:
    a: "DoesNotExist"  # noqa: F821


def _real_context(strict=True) -> DeserializeContext:
    return DeserializeContext(strict=strict, build_value=build_value)


def _fake_context(strict=True):
    """A context whose dispatcher only records the calls."""
    calls = []

    def fake_build_value(data, annotation, location, context):
        calls.append((data, annotation, location))
        return data

    return DeserializeContext(strict=strict, build_value=fake_build_value), calls


def _build(data, annotation, location=(), strict=True):
    return build_dataclass_value(data, annotation, location, _real_context(strict))


# ---------- the plain cases ----------

def test_a_plain_dataclass():
    assert _build({"a": 1, "b": "x"}, Plain) == Plain(1, "x")


def test_nested_dataclasses_and_lists_of_them():
    data = {"inner": {"x": 1}, "items": [{"x": 2}, {"x": 3}]}

    assert _build(data, Outer) == Outer(Inner(1), [Inner(2), Inner(3)])


def test_a_mapping_that_is_not_a_dict_is_accepted_as_data():
    assert _build(MappingProxyType({"a": 1, "b": "x"}), Plain) == Plain(1, "x")


def test_a_frozen_slots_dataclass():
    assert _build({"a": 1}, FrozenSlots) == FrozenSlots(1)


def test_a_keyword_only_field():
    assert _build({"a": 1}, KeywordOnly) == KeywordOnly(a=1)


def test_every_field_is_built_against_its_own_annotation_below_its_name():
    context, calls = _fake_context()

    build_dataclass_value({"a": 1, "b": "x"}, Plain, ("rows", 0), context)

    assert calls == [(1, int, ("rows", 0, "a")), ("x", str, ("rows", 0, "b"))]


# ---------- names in the data ----------

def test_a_field_is_read_under_its_alias():
    assert _build({"userName": "ann"}, Aliased) == Aliased("ann")


def test_the_location_names_the_alias_and_the_annotation_is_the_fields_own():
    context, calls = _fake_context()

    build_dataclass_value({"userName": "ann"}, Aliased, (), context)

    assert calls == [("ann", str, ("userName",))]


def test_the_python_name_of_an_aliased_field_is_an_unknown_key():
    with pytest.raises(DeserializationError) as caught:
        _build({"user_name": "ann"}, Aliased)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"


# ---------- excluded and derived fields ----------

def test_an_excluded_field_comes_from_its_default():
    assert _build({"name": "ann"}, WithSecret) == WithSecret("ann", "none")


def test_an_excluded_field_in_the_data_is_an_unknown_key_when_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"name": "ann", "secret": "x"}, WithSecret)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert caught.value.value == ["secret"]


def test_an_excluded_field_in_the_data_is_ignored_when_not_strict():
    assert _build({"name": "ann", "secret": "x"}, WithSecret, strict=False) == WithSecret("ann", "none")


def test_an_excluded_field_without_a_default_is_reported_missing_by_its_attribute_name():
    with pytest.raises(DeserializationError) as caught:
        _build({}, Unbuildable)

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.value == ["secret"]


def test_a_derived_field_may_be_in_the_data_and_is_never_passed_in():
    result = _build({"a": 1, "computed": 99}, WithDerived)

    assert result == WithDerived(1)
    assert result.computed == 7


def test_a_derived_field_may_be_left_out_of_the_data():
    assert _build({"a": 1}, WithDerived).computed == 7


# ---------- defaults ----------

def test_a_missing_field_with_a_default_takes_the_default():
    result = _build({"a": 1}, WithDefaults)

    assert result == WithDefaults(1, 5, [], None)


def test_a_default_factory_makes_a_new_value_every_time():
    first = _build({"a": 1}, WithDefaults)
    second = _build({"a": 1}, WithDefaults)

    assert first.tags == [] and first.tags is not second.tags


def test_a_field_in_the_data_wins_over_its_default_even_when_it_is_none():
    assert _build({"a": 1, "b": 9, "note": None}, WithDefaults) == WithDefaults(1, 9, [], None)


# ---------- generic and forward references ----------

def test_a_parameterized_generic_builds_by_the_given_type():
    assert _build({"item": 1, "items": [2, 3]}, Box[int]) == Box(1, [2, 3])


def test_a_parameterized_generic_rejects_the_wrong_type_at_the_field():
    with pytest.raises(DeserializationError) as caught:
        _build({"item": "x", "items": []}, Box[int])

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.item"


def test_a_bare_generic_lets_anything_through():
    assert _build({"item": "x", "items": [1, "a"]}, Box) == Box("x", [1, "a"])


def test_a_forward_reference_is_resolved():
    assert _build({"child": {"value": 1}}, Parent) == Parent(Child(1))


def test_an_unresolvable_annotation_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1}, Unresolvable, ("row",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.row"
    assert isinstance(caught.value.__cause__, NameError)


# ---------- rules ----------

def test_an_annotated_field_whose_rule_passes():
    assert _build({"port": 80}, WithRule) == WithRule(80)


def test_an_annotated_field_whose_rule_fails_is_located_at_the_field():
    with pytest.raises(DeserializationError) as caught:
        _build({"port": -1}, WithRule)

    assert caught.value.error_name == "DESERIALIZE_RULE_FAILED"
    assert caught.value.label == "$.port"
    assert caught.value.value == -1


# ---------- unknown and missing ----------

def test_an_unknown_key_is_an_error_when_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1, "b": "x", "c": 2}, Plain, ("row",))

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert caught.value.label == "$.row"
    assert caught.value.value == ["c"]


def test_an_unknown_key_is_ignored_when_not_strict():
    assert _build({"a": 1, "b": "x", "c": 2}, Plain, strict=False) == Plain(1, "x")


def test_a_missing_field_is_an_error_and_names_every_missing_one_in_order():
    with pytest.raises(DeserializationError) as caught:
        _build({}, Plain, ("row",))

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.label == "$.row"
    assert caught.value.value == ["a", "b"]


def test_a_typo_is_reported_as_unknown_together_with_what_is_missing():
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1, "bb": "x"}, Plain)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"
    assert caught.value.value == ["bb"]
    assert "Required but absent: 'b'" in str(caught.value.problem)


def test_a_typo_is_a_missing_field_when_not_strict():
    with pytest.raises(DeserializationError) as caught:
        _build({"a": 1, "bb": "x"}, Plain, strict=False)

    assert caught.value.error_name == "DESERIALIZE_MISSING_FIELD"
    assert caught.value.value == ["b"]


# ---------- data that is no object ----------

@pytest.mark.parametrize("data", [[1], "abc", 5, None], ids=["list", "text", "int", "none"])
def test_data_that_is_not_an_object_is_a_wrong_type_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, Plain, ("row",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.row"
    assert caught.value.value == data


# ---------- locations ----------

def test_a_nested_value_that_does_not_fit_has_the_full_location():
    with pytest.raises(DeserializationError) as caught:
        _build({"inner": {"x": "bad"}, "items": []}, Outer)

    assert caught.value.label == "$.inner.x"


def test_an_item_of_a_list_of_dataclasses_has_the_index_in_its_location():
    with pytest.raises(DeserializationError) as caught:
        _build({"inner": {"x": 1}, "items": [{"x": 1}, {"x": "bad"}]}, Outer)

    assert caught.value.label == "$.items[1].x"


# ---------- a constructor that refuses ----------

def test_a_rejecting_post_init_is_a_build_failed_card_with_the_cause_kept():
    with pytest.raises(DeserializationError) as caught:
        _build({"value": -1}, Rejecting, ("row",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.row"
    assert isinstance(caught.value.__cause__, ValueError)


def test_a_library_error_raised_by_the_constructor_passes_through_unchanged():
    with pytest.raises(DeserializationError) as caught:
        _build({"value": 1}, RaisingCard)

    assert caught.value is _CARD
