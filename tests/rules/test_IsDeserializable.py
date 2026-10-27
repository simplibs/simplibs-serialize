from dataclasses import dataclass
from typing import Annotated

import pytest
from simplibs.exception.testing import Kwargs, assert_exception_function
from simplibs.rules.testing.asserts.assert_rule_describe import assert_rule_describe
from simplibs.rules.testing.asserts.assert_rule_is_valid import assert_rule_is_valid
from simplibs.rules.testing.asserts.assert_rule_param_error import assert_rule_param_error
from simplibs.rules.testing.asserts.assert_rule_slots import assert_rule_slots

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic._common_helpers import describe_annotation
from simplibs.serialize.rules import IsDeserializable


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Server:
    host: str
    port: int


@dataclass
class Config:
    servers: list[Server]


def _positive(value) -> bool:
    return value > 0


_VALID = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
_INVALID = [{"x": 1}, [1], {"x": "a", "y": 2}, {"x": 1, "y": 2, "z": 3}, None, "text", 5]


def _build(rule):
    """Raise whatever build_exception returns, the way `validate` does."""

    def raising_wrapper(target, **options):
        raise rule.build_exception(target, **options)

    return raising_wrapper


# ---------- the parts of the rule contract that apply ----------
# `assert_rule_contract` and its build_exception / validate blades expect a `ValidationError`
# card, while this rule's card is a `DeserializationError` (see the card tests below).

def test_is_deserializable_is_valid(subtests) -> None:
    assert_rule_is_valid(subtests, IsDeserializable(Point), _VALID, _INVALID, verbose=False)


def test_is_deserializable_describe(subtests) -> None:
    expected = f"data for {describe_annotation(Point)}"

    assert_rule_describe(subtests, IsDeserializable(Point), expected_text=expected, verbose=False)


def test_is_deserializable_describe_names_the_annotation() -> None:
    assert "Point" in IsDeserializable(Point).describe()
    assert IsDeserializable(list[Point]).describe() != IsDeserializable(Point).describe()


def test_is_deserializable_slots(subtests) -> None:
    assert_rule_slots(subtests, IsDeserializable(Point), verbose=False)


def test_is_deserializable_constructor_guard(subtests) -> None:
    assert_rule_param_error(
        subtests,
        IsDeserializable,
        [
            ((Point,), {"strict": "yes"}),
            ((Point,), {"strict": 1}),
            ((Point,), {"strict": None}),
        ],
        verbose=False,
    )


# ---------- the parameters ----------

def test_is_deserializable_stores_its_parameters() -> None:
    rule = IsDeserializable(Point, strict=False)

    assert rule.annotation is Point
    assert rule.strict is False


def test_is_deserializable_is_strict_by_default() -> None:
    assert IsDeserializable(Point).strict is True


def test_strict_decides_about_unknown_keys() -> None:
    data = {"x": 1, "y": 2, "z": 3}

    assert IsDeserializable(Point).is_valid(data) is False
    assert IsDeserializable(Point, strict=False).is_valid(data) is True


def test_the_annotation_is_not_checked_when_the_rule_is_built() -> None:
    rule = IsDeserializable(5)

    assert rule.is_valid({"x": 1}) is False


def test_an_unsupported_annotation_accepts_nothing() -> None:
    rule = IsDeserializable(complex)

    assert rule.is_valid(1) is False
    assert rule.build_exception(1).__cause__.error_name == "DESERIALIZE_UNSUPPORTED_ANNOTATION"


def test_a_rule_inside_annotated_decides_too() -> None:
    rule = IsDeserializable(Annotated[int, _positive])

    assert rule.is_valid(5) is True
    assert rule.is_valid(-5) is False


# ---------- validate ----------

def test_validate_passes_valid_data_in_every_mode() -> None:
    rule = IsDeserializable(Point)
    data = {"x": 1, "y": 2}

    assert rule.validate(data) is True
    assert rule.validate(data, return_value=True) is data


def test_validate_returns_false_in_bool_mode_for_invalid_data() -> None:
    assert IsDeserializable(Point).validate({"x": 1}, return_bool=True) is False


def test_validate_raises_the_deserialization_card_for_invalid_data() -> None:
    with pytest.raises(DeserializationError) as caught:
        IsDeserializable(Point).validate({"x": 1}, value_name="point")

    assert caught.value.error_name == "IS_DESERIALIZABLE_ERROR"
    assert caught.value.label == "point"


# ---------- the card ----------

def test_the_card_names_the_data_and_the_annotation(subtests) -> None:
    bad = {"servers": [{"host": "a", "port": 1}, {"host": "b", "port": 2}, {"host": "c", "port": "x"}]}
    wanted = describe_annotation(Config)

    exc = assert_exception_function(
        subtests,
        func=_build(IsDeserializable(Config)),
        invalid_params=(bad, Kwargs(value_name="config", context="step")),
        exception_type=DeserializationError,
        error_name="IS_DESERIALIZABLE_ERROR",
        label="config",
        value=bad,
        expected=f"Data that fits {wanted}.",
        problem=f"step: The data cannot be built into {wanted}; see the cause for the exact location.",
        how_to_fix=(
            "Correct the part named by the cause.",
            "Or pass strict=False to ignore keys the type does not know.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The card is catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)


def test_the_card_without_a_name_and_a_context_has_a_plain_label_and_no_prefix(subtests) -> None:
    exc = assert_exception_function(
        subtests,
        func=_build(IsDeserializable(Point)),
        invalid_params=({"x": 1},),
        exception_type=DeserializationError,
        error_name="IS_DESERIALIZABLE_ERROR",
        label="value",
        problem="The data cannot be built into",
        verbose=False,
    )

    assert not str(exc.problem).startswith(":")


@pytest.mark.parametrize(
    "annotation, bad, cause_name, cause_label",
    [
        pytest.param(Point, [1], "DESERIALIZE_WRONG_TYPE", "$", id="wrong_shape"),
        pytest.param(Point, {"x": 1}, "DESERIALIZE_MISSING_FIELD", "$", id="missing_field"),
        pytest.param(Point, {"x": 1, "y": 2, "z": 3}, "DESERIALIZE_UNKNOWN_FIELD", "$", id="unknown_field"),
        pytest.param(Point, {"x": "a", "y": 2}, "DESERIALIZE_WRONG_TYPE", "$.x", id="wrong_type_inside"),
        pytest.param(
            Config,
            {"servers": [{"host": "a", "port": 1}, {"host": "b", "port": 2}, {"host": "c", "port": "x"}]},
            "DESERIALIZE_WRONG_TYPE",
            "$.servers[2].port",
            id="deep_location",
        ),
        pytest.param(Annotated[int, _positive], -1, "DESERIALIZE_RULE_FAILED", "$", id="rule_violation"),
    ],
)
def test_the_cause_of_the_card_is_the_exact_deserialization_error(annotation, bad, cause_name, cause_label) -> None:
    exc = IsDeserializable(annotation).build_exception(bad)

    assert isinstance(exc.__cause__, DeserializationError)
    assert exc.__cause__.error_name == cause_name
    assert exc.__cause__.label == cause_label


def test_the_card_uses_the_same_strictness_as_the_rule() -> None:
    exc = IsDeserializable(Point, strict=False).build_exception({"x": 1, "zz": 3})

    # Not strict, so the unknown key is no reason; what fails is the missing field
    assert exc.__cause__.error_name == "DESERIALIZE_MISSING_FIELD"


def test_building_the_card_for_valid_data_does_not_raise_and_has_no_cause() -> None:
    exc = IsDeserializable(Point).build_exception({"x": 1, "y": 2})

    assert isinstance(exc, DeserializationError)
    assert exc.__cause__ is None
