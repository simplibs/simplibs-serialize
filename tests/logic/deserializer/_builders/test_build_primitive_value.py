import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_primitive_value


class Port(int):
    """An int subclass."""


class Name(str):
    """A str subclass."""


class Ratio(float):
    """A float subclass."""


class Even(int):
    """An int subclass whose constructor refuses odd numbers."""

    def __new__(cls, value):
        if value % 2:
            raise ValueError("odd number")
        return super().__new__(cls, value)


@pytest.mark.parametrize(
    "data, annotation",
    [
        pytest.param("abc", str, id="text"),
        pytest.param("", str, id="empty_text"),
        pytest.param(5, int, id="int"),
        pytest.param(-5, int, id="negative_int"),
        pytest.param(1.5, float, id="float"),
        pytest.param(True, bool, id="true"),
        pytest.param(False, bool, id="false"),
    ],
)
def test_data_that_is_the_primitive_comes_back_as_it_is(data, annotation):
    result = build_primitive_value(data, annotation, ())

    assert result == data
    assert type(result) is annotation


def test_an_int_stands_for_a_float_and_becomes_one():
    result = build_primitive_value(1, float, ())

    assert result == 1.0
    assert type(result) is float


@pytest.mark.parametrize(
    "data, annotation",
    [
        pytest.param("abc", int, id="text_for_int"),
        pytest.param("1", int, id="numeric_text_for_int"),
        pytest.param(1.0, int, id="float_for_int"),
        pytest.param(True, int, id="bool_for_int"),
        pytest.param(None, int, id="none_for_int"),
        pytest.param(1, bool, id="one_for_bool"),
        pytest.param(0, bool, id="zero_for_bool"),
        pytest.param("true", bool, id="text_for_bool"),
        pytest.param(5, str, id="int_for_str"),
        pytest.param(None, str, id="none_for_str"),
        pytest.param(True, float, id="bool_for_float"),
        pytest.param("1.5", float, id="text_for_float"),
        pytest.param([1], int, id="list_for_int"),
    ],
)
def test_data_of_another_kind_is_a_wrong_type_card(data, annotation):
    with pytest.raises(DeserializationError) as caught:
        build_primitive_value(data, annotation, ("items", 1))

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.items[1]"
    assert caught.value.value == data


@pytest.mark.parametrize(
    "data, annotation",
    [
        pytest.param(8080, Port, id="int_subclass"),
        pytest.param("ann", Name, id="str_subclass"),
        pytest.param(1.5, Ratio, id="float_subclass"),
        pytest.param(2, Even, id="subclass_with_own_constructor"),
    ],
)
def test_a_subclass_is_built_from_the_value(data, annotation):
    result = build_primitive_value(data, annotation, ())

    assert result == data
    assert type(result) is annotation


def test_an_int_stands_for_a_float_in_a_float_subclass_too():
    result = build_primitive_value(1, Ratio, ())

    assert result == 1.0
    assert type(result) is Ratio


def test_a_subclass_still_checks_the_kind_of_the_data():
    with pytest.raises(DeserializationError) as caught:
        build_primitive_value("8080", Port, ())

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"


def test_a_subclass_whose_constructor_refuses_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        build_primitive_value(3, Even, ("port",))

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert caught.value.label == "$.port"
    assert isinstance(caught.value.__cause__, ValueError)


def test_an_int_too_large_for_a_float_is_a_build_failed_card():
    with pytest.raises(DeserializationError) as caught:
        build_primitive_value(10**400, float, ())

    assert caught.value.error_name == "DESERIALIZE_BUILD_FAILED"
    assert isinstance(caught.value.__cause__, OverflowError)
