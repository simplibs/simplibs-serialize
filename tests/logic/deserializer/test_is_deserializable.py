from dataclasses import dataclass
from datetime import date
from typing import Annotated, Literal

import pytest
from simplibs.exception import ParamError

from simplibs.serialize import is_deserializable, serialized_field


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Node:
    child: "Node | None" = None


@dataclass
class BrokenOptions:
    value: int = serialized_field(default=0, metadata={"simplibs.serialize": {"alais": "x"}})


def _positive(value) -> bool:
    return value > 0


@pytest.mark.parametrize(
    "data, annotation",
    [
        pytest.param({"x": 1, "y": 2}, Point, id="dataclass"),
        pytest.param([1, 2], list[int], id="list"),
        pytest.param(None, int | None, id="optional"),
        pytest.param("a", Literal["a", "b"], id="literal"),
        pytest.param(5, Annotated[int, _positive], id="rule_that_passes"),
        pytest.param("2026-01-02", date, id="date"),
    ],
)
def test_true_for_data_that_fits(data, annotation):
    assert is_deserializable(data, annotation) is True


@pytest.mark.parametrize(
    "data, annotation",
    [
        pytest.param([1], Point, id="wrong_shape"),
        pytest.param({"x": "a", "y": 2}, Point, id="wrong_type_inside"),
        pytest.param(-1, Annotated[int, _positive], id="rule_violation"),
        pytest.param({"x": 1}, Point, id="missing_field"),
        pytest.param({"x": 1, "y": 2, "z": 3}, Point, id="unknown_key_when_strict"),
        pytest.param("c", Literal["a", "b"], id="literal_mismatch"),
        pytest.param(None, int | str, id="union_without_a_match"),
        pytest.param("not a date", date, id="text_that_is_no_date"),
        pytest.param(1, complex, id="unsupported_annotation"),
    ],
)
def test_false_for_data_that_does_not_fit(data, annotation):
    assert is_deserializable(data, annotation) is False


def test_strict_decides_about_unknown_keys():
    data = {"x": 1, "y": 2, "z": 3}

    assert is_deserializable(data, Point) is False
    assert is_deserializable(data, Point, strict=False) is True


def test_false_for_data_nested_beyond_the_limit():
    data: dict = {}
    for _ in range(100_000):
        data = {"child": data}

    assert is_deserializable(data, Node) is False


def test_a_param_error_is_a_bug_in_the_class_and_passes_through():
    with pytest.raises(ParamError):
        is_deserializable({"value": 1}, BrokenOptions)
