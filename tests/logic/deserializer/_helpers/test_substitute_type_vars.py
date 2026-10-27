from typing import Annotated, Any, Generic, Optional, TypeVar

import pytest

from simplibs.serialize.logic.deserializer._helpers.substitute_type_vars import substitute_type_vars


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
Bounded = TypeVar("Bounded", bound=int)


class Box(Generic[T]):
    """A generic class."""


@pytest.mark.parametrize(
    "hint, mapping, expected",
    [
        pytest.param(T, {T: int}, int, id="the_variable_itself"),
        pytest.param(list[T], {T: int}, list[int], id="inside_a_list"),
        pytest.param(dict[str, T], {T: int}, dict[str, int], id="inside_a_dict_value"),
        pytest.param(list[dict[str, T]], {T: int}, list[dict[str, int]], id="nested"),
        pytest.param(T | None, {T: int}, int | None, id="inside_an_optional"),
        pytest.param(Annotated[T, "rule"], {T: int}, Annotated[int, "rule"], id="inside_annotated"),
        pytest.param(dict[K, V], {K: str, V: int}, dict[str, int], id="two_variables"),
        pytest.param(T, {T: list[int]}, list[int], id="replaced_by_a_subscripted_annotation"),
    ],
)
def test_replaces_the_variables(hint, mapping, expected):
    assert substitute_type_vars(hint, mapping) == expected


def test_a_variable_that_is_not_in_the_mapping_becomes_any():
    assert substitute_type_vars(T, {}) is Any


def test_a_variable_that_is_not_in_the_mapping_becomes_its_bound():
    assert substitute_type_vars(Bounded, {}) is int


def test_a_variable_missing_from_a_larger_annotation_becomes_any():
    assert substitute_type_vars(dict[K, V], {K: str}) == dict[str, Any]


def test_an_optional_variable_that_is_not_in_the_mapping_becomes_an_optional_any():
    assert substitute_type_vars(T | None, {}) == Optional[Any]


@pytest.mark.parametrize(
    "hint",
    [int, str, list[int], dict[str, int], int | None, Box, Annotated[int, "rule"]],
    ids=["int", "str", "subscripted_list", "subscripted_dict", "optional", "generic_class", "annotated"],
)
def test_an_annotation_without_variables_is_returned_unchanged(hint):
    assert substitute_type_vars(hint, {T: int}) is hint
