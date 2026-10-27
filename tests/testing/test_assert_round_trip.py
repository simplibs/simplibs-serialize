import math
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import count

import pytest

from simplibs.serialize import register_type
from simplibs.serialize.testing import assert_round_trip


_VALID_JSON = "serialize returns valid JSON-compatible data"
_SAME_DATA = "serialize returns the same data every time"
_STRUCTURE = "deserialize(serialize(value)) equals the value"
_JSON_TEXT = "from_json(to_json(value)) equals the value"


class RecordingSubtests:
    """Stands in for the pytest-subtests fixture and only writes down how each check ended.

    The real fixture catches a failing check, reports it and lets the test go on. This one
    does the same, so a test can look at the outcome of the helper instead of failing itself.
    """

    def __init__(self) -> None:
        self.results: list[tuple[str, Exception | None]] = []

    @contextmanager
    def test(self, msg=None, **kwargs):
        try:
            yield
        except Exception as error:
            self.results.append((msg, error))
        else:
            self.results.append((msg, None))

    @property
    def names(self) -> list[str]:
        return [name for name, _ in self.results]

    @property
    def failed(self) -> list[str]:
        return [name for name, error in self.results if error is not None]

    def error_of(self, name: str) -> Exception:
        return dict(self.results)[name]


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Money:
    amount: int


@dataclass
class Measure:
    value: float


class Counted:
    """A type whose handler gives different data on every call."""


# ---------- a value that passes ----------

def test_a_passing_value_runs_all_four_checks_and_all_pass():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Point(1, 2))

    assert subtests.names == [_VALID_JSON, _SAME_DATA, _STRUCTURE, _JSON_TEXT]
    assert subtests.failed == []


def test_it_works_with_the_real_fixture(subtests):
    assert_round_trip(subtests, Point(1, 2))


def test_it_returns_nothing():
    assert assert_round_trip(RecordingSubtests(), Point(1, 2)) is None


@pytest.mark.parametrize(
    "value",
    [5, "text", None, [1, 2], {"a": [1]}, {"b", "a"}, (1, "a")],
    ids=["int", "text", "none", "list", "dict", "set", "tuple"],
)
def test_plain_values_pass_with_the_type_of_the_value(value):
    subtests = RecordingSubtests()

    assert_round_trip(subtests, value, None if value is not None else type(None))

    assert subtests.failed == []


def test_a_set_of_text_is_the_same_every_time():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, {"b", "a", "c", "d", "e", "f"})

    assert _SAME_DATA in subtests.names
    assert subtests.failed == []


# ---------- the annotation ----------

def test_without_an_annotation_the_type_of_the_value_is_built_so_a_list_of_dataclasses_fails():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, [Point(1, 2)])

    # `type(value)` is just `list`, so the points come back as plain dicts
    assert subtests.failed == [_STRUCTURE, _JSON_TEXT]


def test_an_annotation_makes_a_list_of_dataclasses_pass():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, [Point(1, 2), Point(3, 4)], list[Point])

    assert subtests.failed == []


def test_an_annotation_for_a_dict_with_optional_values():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, {"a": 1, "b": None}, dict[str, int | None])

    assert subtests.failed == []


# ---------- check_json ----------

def test_check_json_off_leaves_out_the_text_check():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Point(1, 2), check_json=False)

    assert subtests.names == [_VALID_JSON, _SAME_DATA, _STRUCTURE]
    assert subtests.failed == []


# ---------- strict ----------

def test_strict_off_is_accepted():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Point(1, 2), strict=False)

    assert subtests.failed == []


# ---------- compare ----------

def test_a_nan_inside_a_value_needs_its_own_compare():
    register_type(
        Measure,
        to_func=lambda measure: {"value": None if math.isnan(measure.value) else measure.value},
        from_func=lambda data, annotation: Measure(float("nan") if data["value"] is None else data["value"]),
    )
    # A fresh nan each time: `math.nan` is one shared object, which equality treats as the same
    value = Measure(float("nan"))

    plain = RecordingSubtests()
    assert_round_trip(plain, value)
    assert plain.failed == [_STRUCTURE, _JSON_TEXT]

    custom = RecordingSubtests()
    assert_round_trip(
        custom,
        value,
        compare=lambda left, right: math.isnan(left.value) and math.isnan(right.value),
    )
    assert custom.failed == []


def test_compare_replaces_equality_in_both_round_trips():
    calls = []

    def compare(left, right):
        calls.append((left, right))
        return True

    assert_round_trip(RecordingSubtests(), Point(1, 2), compare=compare)

    assert calls == [(Point(1, 2), Point(1, 2))] * 2


# ---------- a failure is reported, not raised ----------

def test_a_handler_pair_that_does_not_invert_each_other_is_reported_not_raised():
    register_type(
        Money,
        to_func=lambda money: {"amount": money.amount},
        from_func=lambda data, annotation: Money(data["amount"] + 1),
    )
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Money(5))

    assert subtests.failed == [_STRUCTURE, _JSON_TEXT]
    error = subtests.error_of(_STRUCTURE)
    assert isinstance(error, AssertionError)
    assert "expected Money(amount=5), got Money(amount=6)" in str(error)


def test_a_handler_that_gives_different_data_each_time_is_caught_by_the_second_check():
    numbers = count()
    register_type(Counted, to_func=lambda obj: next(numbers))
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Counted(), check_json=False)

    assert _SAME_DATA in subtests.failed
    assert "two calls gave different data" in str(subtests.error_of(_SAME_DATA))


def test_a_handler_that_returns_something_json_rejects_is_caught_by_the_first_check():
    register_type(Counted, to_func=lambda obj: {"x": float("nan")})
    subtests = RecordingSubtests()

    assert_round_trip(subtests, Counted())

    assert _VALID_JSON in subtests.failed


def test_when_serialize_fails_the_other_checks_are_skipped():
    subtests = RecordingSubtests()

    assert_round_trip(subtests, object())

    assert subtests.names == [_VALID_JSON]
    assert subtests.failed == [_VALID_JSON]
