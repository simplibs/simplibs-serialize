from dataclasses import dataclass
from datetime import date
from enum import Enum

import pytest
from simplibs.exception.testing import Kwargs, assert_exception_function
from simplibs.rules.testing.asserts.assert_rule_describe import assert_rule_describe
from simplibs.rules.testing.asserts.assert_rule_is_valid import assert_rule_is_valid
from simplibs.rules.testing.asserts.assert_rule_param_error import assert_rule_param_error
from simplibs.rules.testing.asserts.assert_rule_slots import assert_rule_slots

from simplibs.serialize import SerializationError, register_type
from simplibs.serialize.rules import IsSerializable


@dataclass
class Point:
    x: int
    y: int


class Color(Enum):
    RED = "red"


class Unknown:
    """Nothing knows this class."""


def _cycle() -> list:
    """A list that contains itself."""
    data: list = []
    data.append(data)
    return data


_VALID = [None, 5, "a", [1, {"a": 2}], {1, 2}, Point(1, 2), date(2026, 1, 2), Color.RED, b"hi"]
_INVALID = [
    Unknown(),
    float("nan"),
    [float("inf")],
    _cycle(),
    {(1, 2): 1},
    {"a": [Unknown()]},
]


def _build(rule):
    """Raise whatever build_exception returns, the way `validate` does."""

    def raising_wrapper(target, **options):
        raise rule.build_exception(target, **options)

    return raising_wrapper


# ---------- the parts of the rule contract that apply ----------
# `assert_rule_contract` and its build_exception / validate blades expect a `ValidationError`
# card, while this rule's card is a `SerializationError` (see the card tests below).

def test_is_serializable_is_valid(subtests) -> None:
    assert_rule_is_valid(subtests, IsSerializable(), _VALID, _INVALID, verbose=False)


def test_is_serializable_describe(subtests) -> None:
    assert_rule_describe(subtests, IsSerializable(), expected_text="serializable value", verbose=False)


def test_is_serializable_slots(subtests) -> None:
    assert_rule_slots(subtests, IsSerializable(), verbose=False)


def test_is_serializable_constructor_guard(subtests) -> None:
    assert_rule_param_error(
        subtests,
        IsSerializable,
        [
            ((), {"default": 5}),
            ((), {"default": "text"}),
            ((), {"allow_nan": "yes"}),
            ((), {"allow_nan": 1}),
        ],
        verbose=False,
    )


# ---------- the parameters ----------

def test_is_serializable_stores_its_parameters() -> None:
    handler = lambda obj: "unknown"

    rule = IsSerializable(default=handler, allow_nan=True)

    assert rule.default is handler
    assert rule.allow_nan is True


def test_is_serializable_defaults() -> None:
    rule = IsSerializable()

    assert rule.default is None
    assert rule.allow_nan is False


def test_is_serializable_default_makes_an_unknown_type_valid() -> None:
    assert IsSerializable().is_valid(Unknown()) is False
    assert IsSerializable(default=lambda obj: "unknown").is_valid(Unknown()) is True


def test_is_serializable_allow_nan_makes_a_nan_valid() -> None:
    assert IsSerializable().is_valid(float("nan")) is False
    assert IsSerializable(allow_nan=True).is_valid(float("nan")) is True


def test_is_serializable_agrees_with_a_registered_type() -> None:
    register_type(Unknown, to_func=lambda obj: "registered")

    assert IsSerializable().is_valid([Unknown()]) is True


# ---------- validate ----------

def test_validate_passes_a_valid_value_in_every_mode() -> None:
    rule = IsSerializable()
    value = {"a": [1]}

    assert rule.validate(value) is True
    assert rule.validate(value, return_value=True) is value


def test_validate_returns_false_in_bool_mode_for_an_invalid_value() -> None:
    assert IsSerializable().validate(Unknown(), return_bool=True) is False


def test_validate_raises_the_serialization_card_for_an_invalid_value() -> None:
    with pytest.raises(SerializationError) as caught:
        IsSerializable().validate(Unknown(), value_name="payload")

    assert caught.value.error_name == "IS_SERIALIZABLE_ERROR"
    assert caught.value.label == "payload"


# ---------- the card ----------

def test_the_card_names_the_value_and_where_it_was_met(subtests) -> None:
    bad = {"items": [1, Unknown()]}

    exc = assert_exception_function(
        subtests,
        func=_build(IsSerializable()),
        invalid_params=(bad, Kwargs(value_name="payload", context="step")),
        exception_type=SerializationError,
        error_name="IS_SERIALIZABLE_ERROR",
        label="payload",
        value=bad,
        expected="A value serialize() can convert.",
        problem="step: The value cannot be converted by serialize(); see the cause for the exact location.",
        how_to_fix=(
            "Fix the part named by the cause (a type to register, a cycle, a NaN).",
            "Or pass `default=` to deal with unknown objects in one place.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The card is catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)


def test_the_card_without_a_name_and_a_context_has_a_plain_label_and_no_prefix(subtests) -> None:
    exc = assert_exception_function(
        subtests,
        func=_build(IsSerializable()),
        invalid_params=(Unknown(),),
        exception_type=SerializationError,
        error_name="IS_SERIALIZABLE_ERROR",
        label="value",
        problem="The value cannot be converted by serialize()",
        verbose=False,
    )

    assert not str(exc.problem).startswith(":")


@pytest.mark.parametrize(
    "bad, cause_name, cause_label",
    [
        pytest.param({"items": [1, Unknown()]}, "SERIALIZE_UNSUPPORTED_TYPE", "$.items[1]", id="unknown_type"),
        pytest.param(_cycle(), "SERIALIZE_CIRCULAR_REFERENCE", "$[0]", id="circle"),
        pytest.param({"price": float("nan")}, "SERIALIZE_NON_FINITE_NUMBER", "$.price", id="nan"),
        pytest.param({(1, 2): 1}, "SERIALIZE_UNSUPPORTED_KEY", "$", id="key_without_a_text_form"),
        pytest.param({1: "a", "1": "b"}, "SERIALIZE_DUPLICATE_KEY", "$", id="duplicate_key"),
    ],
)
def test_the_cause_of_the_card_is_the_exact_serialization_error(bad, cause_name, cause_label) -> None:
    exc = IsSerializable().build_exception(bad)

    assert isinstance(exc.__cause__, SerializationError)
    assert exc.__cause__.error_name == cause_name
    assert exc.__cause__.label == cause_label


def test_the_cause_comes_from_a_failing_handler_too() -> None:
    register_type(Unknown, to_func=lambda obj: 1 / 0)

    exc = IsSerializable().build_exception([Unknown()])

    assert exc.__cause__.error_name == "SERIALIZE_HANDLER_FAILED"
    assert exc.__cause__.label == "$[0]"
    assert isinstance(exc.__cause__.__cause__, ZeroDivisionError)


def test_the_card_uses_the_same_options_as_the_rule() -> None:
    exc = IsSerializable(allow_nan=True).build_exception({"a": Unknown(), "b": float("nan")})

    # nan is allowed here, so the first thing that fails is the unknown type
    assert exc.__cause__.error_name == "SERIALIZE_UNSUPPORTED_TYPE"
    assert exc.__cause__.label == "$.a"


def test_building_the_card_for_a_valid_value_does_not_raise_and_has_no_cause() -> None:
    exc = IsSerializable().build_exception({"a": 1})

    assert isinstance(exc, SerializationError)
    assert exc.__cause__ is None
