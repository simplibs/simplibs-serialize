import typing

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_tuple_value, build_value
from simplibs.serialize.logic.deserializer._classes import DeserializeContext


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
    return build_tuple_value(data, annotation, location, _real_context())


# ---------- the three shapes ----------

@pytest.mark.parametrize(
    "annotation",
    [tuple, typing.Tuple],
    ids=["tuple", "typing_Tuple"],
)
def test_a_bare_tuple_takes_any_length_and_any_items(annotation):
    result = _build([1, "a", None], annotation)

    assert result == (1, "a", None)
    assert type(result) is tuple


@pytest.mark.parametrize(
    "data, expected",
    [pytest.param([1, 2, 3], (1, 2, 3), id="several"), pytest.param([], (), id="empty"), pytest.param([7], (7,), id="one")],
)
def test_a_homogeneous_tuple_takes_any_length_of_one_type(data, expected):
    assert _build(data, tuple[int, ...]) == expected


@pytest.mark.parametrize(
    "annotation",
    [tuple[int, str], typing.Tuple[int, str]],
    ids=["tuple", "typing_Tuple"],
)
def test_a_positional_tuple_builds_each_position_by_its_own_annotation(annotation):
    result = _build([1, "a"], annotation)

    assert result == (1, "a")
    assert type(result) is tuple


def test_a_tuple_of_data_is_accepted_as_a_list():
    assert _build((1, 2), tuple[int, int]) == (1, 2)


# ---------- the empty tuple ----------

def test_the_empty_tuple_annotation_takes_only_an_empty_list():
    assert _build([], tuple[()]) == ()


def test_the_empty_tuple_annotation_refuses_any_item():
    with pytest.raises(DeserializationError) as caught:
        _build([1], tuple[()], ("pair",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_LENGTH"
    assert caught.value.label == "$.pair"


# ---------- wrong length ----------

@pytest.mark.parametrize(
    "data",
    [[1], [1, "a", "b"], []],
    ids=["too_short", "too_long", "empty"],
)
def test_a_positional_tuple_of_the_wrong_length_is_a_wrong_length_card(data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, tuple[int, str], ("pair",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_LENGTH"
    assert caught.value.label == "$.pair"
    assert caught.value.value == data


# ---------- wrong kind of data ----------

@pytest.mark.parametrize(
    "data",
    ["abc", {"a": 1}, 5, None],
    ids=["text", "object", "int", "none"],
)
@pytest.mark.parametrize("annotation", [tuple, tuple[int, ...], tuple[int, str]], ids=["bare", "homogeneous", "positional"])
def test_data_that_is_not_a_list_is_a_wrong_type_card(annotation, data):
    with pytest.raises(DeserializationError) as caught:
        _build(data, annotation, ("pair",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.pair"
    assert caught.value.value == data


# ---------- locations ----------

def test_every_position_is_built_below_its_index_by_its_annotation():
    context, calls = _fake_context()

    build_tuple_value([1, "a"], tuple[int, str], ("rows", 0), context)

    assert calls == [(1, int, ("rows", 0, 0)), ("a", str, ("rows", 0, 1))]


def test_a_homogeneous_tuple_builds_every_item_by_the_same_annotation():
    context, calls = _fake_context()

    build_tuple_value([1, 2], tuple[int, ...], (), context)

    assert calls == [(1, int, (0,)), (2, int, (1,))]


def test_an_item_that_does_not_fit_is_located_by_its_index():
    with pytest.raises(DeserializationError) as caught:
        _build(["x", "a"], tuple[int, str], ("pair",))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.pair[0]"
