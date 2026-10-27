from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Optional, Union

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_union_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


@dataclass
class Point:
    x: int
    y: int


@dataclass
class First:
    a: int


@dataclass
class Second:
    b: int


def _positive(value) -> bool:
    return value > 0


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
    return build_union_value(data, annotation, location, _real_context())


# ---------- the member that fits ----------

@pytest.mark.parametrize("annotation", [int | str, Union[int, str]], ids=["pipe", "Union"])
def test_the_member_that_fits_the_data_is_used(annotation):
    assert _build(5, annotation) == 5
    assert _build("a", annotation) == "a"


def test_an_int_fits_both_int_and_float_and_the_int_wins_by_being_exact():
    result = _build(5, int | float)

    assert result == 5
    assert type(result) is int


def test_a_float_fits_only_the_float_member():
    result = _build(5.0, int | float)

    assert result == 5.0
    assert type(result) is float


def test_a_bool_is_a_bool_and_an_int_is_an_int():
    assert _build(True, int | bool) is True
    result = _build(1, int | bool)
    assert result == 1 and type(result) is int


def test_text_fits_str_and_path_and_the_str_wins_by_being_exact():
    assert _build("a/b", str | Path) == "a/b"


def test_a_container_member_is_built():
    assert _build([1, 2], list[int] | int) == [1, 2]
    assert _build(5, list[int] | int) == 5


def test_a_dataclass_is_chosen_by_the_keys_of_the_data():
    assert _build({"a": 1}, First | Second) == First(1)
    assert _build({"b": 2}, First | Second) == Second(2)


def test_three_members_and_none():
    annotation = int | str | None

    assert _build(5, annotation) == 5
    assert _build("a", annotation) == "a"
    assert _build(None, annotation) is None


# ---------- annotated members ----------

def test_a_member_whose_rule_fails_is_not_a_candidate():
    annotation = Annotated[int, _positive] | str

    assert _build(5, annotation) == 5
    assert _build("x", annotation) == "x"
    with pytest.raises(DeserializationError) as caught:
        _build(-1, annotation, ("n",))

    assert caught.value.error_name == "DESERIALIZE_UNION_NO_MATCH"
    assert caught.value.label == "$.n"


def test_the_member_whose_rule_passes_is_chosen():
    annotation = Annotated[int, _positive] | Annotated[int, lambda value: value < 0]

    assert _build(-3, annotation) == -3


# ---------- None ----------

def test_none_is_accepted_when_the_union_contains_none():
    assert _build(None, int | None) is None
    assert _build(None, Optional[int]) is None


def test_none_is_no_answer_for_a_union_without_none():
    with pytest.raises(DeserializationError) as caught:
        _build(None, int | str, ("n",))

    assert caught.value.error_name == "DESERIALIZE_UNION_NO_MATCH"
    assert caught.value.label == "$.n"
    assert caught.value.__cause__ is None


# ---------- Optional is no choice ----------

def test_an_optional_builds_its_only_member_and_nothing_else_is_tried():
    context, calls = _fake_context()

    build_union_value(5, Optional[int], ("n",), context)

    assert calls == [(5, int, ("n",))]


def test_none_for_an_optional_tries_no_member_at_all():
    context, calls = _fake_context()

    build_union_value(None, Optional[int], (), context)

    assert calls == []


def test_the_error_of_an_optional_member_is_its_own_and_deep():
    with pytest.raises(DeserializationError) as caught:
        _build({"x": "bad", "y": 2}, Point | None, ("pt",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.pt.x"


# ---------- no member fits ----------

def test_data_that_fits_no_member_is_a_union_no_match_card_with_the_closest_cause():
    with pytest.raises(DeserializationError) as caught:
        _build([1, "a"], list[int] | dict[str, int], ("n",))

    assert caught.value.error_name == "DESERIALIZE_UNION_NO_MATCH"
    assert caught.value.label == "$.n"
    assert caught.value.value == [1, "a"]
    # The list got deeper into the data than the dict did
    assert isinstance(caught.value.__cause__, DeserializationError)
    assert caught.value.__cause__.label == "$.n[1]"


def test_when_every_member_fails_at_the_same_depth_the_first_is_the_cause():
    with pytest.raises(DeserializationError) as caught:
        _build("x", int | list[int])

    assert caught.value.__cause__.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.__cause__.label == "$"


# ---------- a real tie ----------

def test_an_empty_list_fits_two_list_members_equally_and_is_ambiguous():
    with pytest.raises(DeserializationError) as caught:
        _build([], list[int] | list[str], ("n",))

    assert caught.value.error_name == "DESERIALIZE_UNION_AMBIGUOUS"
    assert caught.value.label == "$.n"
    assert caught.value.value == []


def test_the_same_union_is_not_ambiguous_when_the_items_tell_the_members_apart():
    assert _build([1], list[int] | list[str]) == [1]
    assert _build(["a"], list[int] | list[str]) == ["a"]


def test_a_bare_date_text_fits_date_and_datetime_and_is_ambiguous():
    with pytest.raises(DeserializationError) as caught:
        _build("2026-01-02", date | datetime)

    assert caught.value.error_name == "DESERIALIZE_UNION_AMBIGUOUS"


def test_a_full_datetime_text_fits_only_datetime():
    assert _build("2026-01-02T03:04:05", date | datetime) == datetime(2026, 1, 2, 3, 4, 5)
