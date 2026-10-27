from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any

import pytest
from simplibs.rules import IsTyping

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_annotated_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


def _positive(value) -> bool:
    return value > 0


def _small(value) -> bool:
    return value < 100


class _Marker:
    """A class used as a marker in `Annotated`."""


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
    return build_annotated_value(data, annotation, location, _real_context())


# ---------- a rule that passes and one that fails ----------

@pytest.mark.parametrize(
    "rule",
    [_positive, lambda value: value > 0],
    ids=["function", "lambda"],
)
def test_a_predicate_that_passes_lets_the_value_through(rule):
    assert _build(5, Annotated[int, rule]) == 5


@pytest.mark.parametrize(
    "rule",
    [_positive, lambda value: value > 0],
    ids=["function", "lambda"],
)
def test_a_predicate_that_fails_is_a_rule_failed_card_with_the_value_and_location(rule):
    with pytest.raises(DeserializationError) as caught:
        _build(-5, Annotated[int, rule], ("port",))

    assert caught.value.error_name == "DESERIALIZE_RULE_FAILED"
    assert caught.value.label == "$.port"
    assert caught.value.value == -5


def test_a_rule_object_is_accepted():
    assert _build(5, Annotated[int, IsTyping(int)]) == 5


def test_a_rule_object_that_fails_is_a_rule_failed_card():
    with pytest.raises(DeserializationError) as caught:
        _build("x", Annotated[Any, IsTyping(int)])

    assert caught.value.error_name == "DESERIALIZE_RULE_FAILED"


def test_every_rule_must_pass():
    annotation = Annotated[int, _positive, _small]

    assert _build(50, annotation) == 50
    with pytest.raises(DeserializationError):
        _build(500, annotation)
    with pytest.raises(DeserializationError):
        _build(-5, annotation)


def test_nested_annotated_keeps_the_rules_of_both_levels():
    annotation = Annotated[Annotated[int, _positive], _small]

    assert _build(50, annotation) == 50
    with pytest.raises(DeserializationError):
        _build(-5, annotation)
    with pytest.raises(DeserializationError):
        _build(500, annotation)


# ---------- metadata that is not a rule ----------

@pytest.mark.parametrize(
    "metadata",
    ["documentation", 5, None, ("a", "b"), {"a": 1}, _Marker],
    ids=["text", "number", "none", "tuple", "dict", "marker_class"],
)
def test_metadata_that_is_not_a_rule_is_skipped(metadata):
    assert _build(5, Annotated[int, metadata]) == 5


def test_metadata_that_is_not_a_rule_does_not_stop_a_rule_after_it():
    with pytest.raises(DeserializationError) as caught:
        _build(-5, Annotated[int, "documentation", _positive])

    assert caught.value.error_name == "DESERIALIZE_RULE_FAILED"


# ---------- the type comes first ----------

def test_the_data_is_built_against_the_underlying_type_at_the_same_location():
    context, calls = _fake_context()

    build_annotated_value(5, Annotated[int, _positive], ("port",), context)

    assert calls == [(5, int, ("port",))]


def test_data_of_the_wrong_type_fails_before_any_rule_runs():
    seen = []

    def spy(value):
        seen.append(value)
        return True

    with pytest.raises(DeserializationError) as caught:
        _build("x", Annotated[int, spy])

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert seen == []


def test_a_rule_gets_the_built_value_not_the_data():
    seen = []

    def spy(value):
        seen.append(value)
        return True

    _build("2026-01-02", Annotated[date, spy])

    assert seen == [date(2026, 1, 2)]


# ---------- a rule that raises ----------

def test_a_rule_that_raises_is_a_card_with_the_location():
    with pytest.raises(DeserializationError) as caught:
        _build(5, Annotated[int, lambda value: 1 / 0], ("port",))

    # Whether the validation library reports a raising rule as a failure or lets it
    # out, the caller meets one card at the right place
    assert caught.value.error_name in {"DESERIALIZE_BUILD_FAILED", "DESERIALIZE_RULE_FAILED"}
    assert caught.value.label == "$.port"


# ---------- inside other annotations ----------

@dataclass
class Server:
    port: Annotated[int, _positive]
    names: list[Annotated[str, lambda text: bool(text)]]


def test_rules_inside_a_list_are_checked_per_item():
    annotation = list[Annotated[int, _positive]]

    assert build_value([1, 2], annotation, (), _real_context()) == [1, 2]
    with pytest.raises(DeserializationError) as caught:
        build_value([1, -2], annotation, (), _real_context())

    assert caught.value.error_name == "DESERIALIZE_RULE_FAILED"
    assert caught.value.label == "$[1]"


def test_rules_inside_a_dict_are_checked_per_value():
    with pytest.raises(DeserializationError) as caught:
        build_value({"a": 1, "b": -2}, dict[str, Annotated[int, _positive]], (), _real_context())

    assert caught.value.label == "$.b"


def test_rules_on_the_fields_of_a_dataclass_are_checked():
    assert build_value({"port": 80, "names": ["a"]}, Server, (), _real_context()) == Server(80, ["a"])
    with pytest.raises(DeserializationError) as caught:
        build_value({"port": 80, "names": ["a", ""]}, Server, (), _real_context())

    assert caught.value.label == "$.names[1]"
