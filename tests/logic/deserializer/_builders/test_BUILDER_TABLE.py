import types
import typing
from collections import OrderedDict, deque
from collections import abc
from typing import Annotated, Final, Literal, NotRequired, Required, Union, get_origin

import pytest

from simplibs.serialize.logic.deserializer._builders import (
    BUILDER_TABLE,
    build_annotated_value,
    build_elements_value,
    build_literal_value,
    build_mapping_value,
    build_qualified_value,
    build_tuple_value,
    build_union_value,
)


_EXPECTED = {
    list: build_elements_value,
    set: build_elements_value,
    frozenset: build_elements_value,
    deque: build_elements_value,
    abc.Sequence: build_elements_value,
    abc.MutableSequence: build_elements_value,
    abc.Collection: build_elements_value,
    abc.Iterable: build_elements_value,
    abc.Set: build_elements_value,
    abc.MutableSet: build_elements_value,
    tuple: build_tuple_value,
    dict: build_mapping_value,
    OrderedDict: build_mapping_value,
    abc.Mapping: build_mapping_value,
    abc.MutableMapping: build_mapping_value,
    Union: build_union_value,
    types.UnionType: build_union_value,
    Annotated: build_annotated_value,
    Literal: build_literal_value,
    Final: build_qualified_value,
    Required: build_qualified_value,
    NotRequired: build_qualified_value,
}

if hasattr(typing, "ReadOnly"):
    _EXPECTED[typing.ReadOnly] = build_qualified_value


def test_is_read_only():
    with pytest.raises(TypeError):
        BUILDER_TABLE[int] = build_elements_value


def test_knows_exactly_these_origins():
    assert set(BUILDER_TABLE) == set(_EXPECTED)


@pytest.mark.parametrize(
    "origin",
    list(_EXPECTED),
    ids=lambda origin: getattr(origin, "__name__", None) or repr(origin),
)
def test_every_key_reaches_its_builder(origin):
    assert BUILDER_TABLE[origin] is _EXPECTED[origin]


@pytest.mark.parametrize(
    "subscripted, bare",
    [
        pytest.param(list[int], list, id="list"),
        pytest.param(set[int], set, id="set"),
        pytest.param(frozenset[int], frozenset, id="frozenset"),
        pytest.param(deque[int], deque, id="deque"),
        pytest.param(abc.Sequence[int], abc.Sequence, id="Sequence"),
        pytest.param(abc.Set[int], abc.Set, id="Set"),
        pytest.param(tuple[int, ...], tuple, id="tuple"),
        pytest.param(dict[str, int], dict, id="dict"),
        pytest.param(OrderedDict[str, int], OrderedDict, id="OrderedDict"),
        pytest.param(abc.Mapping[str, int], abc.Mapping, id="Mapping"),
    ],
)
def test_a_bare_class_and_a_subscripted_one_reach_the_same_builder(subscripted, bare):
    assert BUILDER_TABLE[get_origin(subscripted)] is BUILDER_TABLE[bare]


@pytest.mark.parametrize(
    "annotation, builder",
    [
        pytest.param(Union[int, str], build_union_value, id="Union"),
        pytest.param(int | str, build_union_value, id="pipe_union"),
        pytest.param(int | None, build_union_value, id="optional"),
        pytest.param(Annotated[int, 1], build_annotated_value, id="Annotated"),
        pytest.param(Literal["a"], build_literal_value, id="Literal"),
        pytest.param(Final[int], build_qualified_value, id="Final"),
        pytest.param(Required[int], build_qualified_value, id="Required"),
        pytest.param(NotRequired[int], build_qualified_value, id="NotRequired"),
    ],
)
def test_the_origin_of_a_special_annotation_reaches_its_builder(annotation, builder):
    assert BUILDER_TABLE[get_origin(annotation)] is builder
