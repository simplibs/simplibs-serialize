from pathlib import Path
from typing import Annotated, Any

import pytest

from simplibs.serialize.logic.deserializer._helpers import is_exact_type_match


@pytest.mark.parametrize(
    "data, member",
    [
        pytest.param(5, int, id="int_is_int"),
        pytest.param(5.0, float, id="float_is_float"),
        pytest.param("x", str, id="text_is_str"),
        pytest.param(True, bool, id="bool_is_bool"),
    ],
)
def test_true_when_the_data_is_exactly_that_primitive(data, member):
    assert is_exact_type_match(data, member) is True


@pytest.mark.parametrize(
    "data, member",
    [
        pytest.param(5, float, id="int_is_not_float"),
        pytest.param(5.0, int, id="float_is_not_int"),
        pytest.param(True, int, id="bool_is_not_int"),
        pytest.param(5, bool, id="int_is_not_bool"),
        pytest.param("x", Path, id="text_is_not_path"),
        pytest.param("x", int, id="text_is_not_int"),
    ],
)
def test_false_when_the_data_is_another_primitive_or_another_class(data, member):
    assert is_exact_type_match(data, member) is False


@pytest.mark.parametrize(
    "data, member",
    [
        pytest.param([1], list[int], id="list_has_no_exact_type"),
        pytest.param([], list, id="bare_list"),
        pytest.param({"a": 1}, dict, id="dict"),
        pytest.param(None, type(None), id="none"),
        pytest.param(5, Any, id="any"),
        pytest.param(5, Annotated[int, [1]], id="unhashable_annotation"),
    ],
)
def test_false_for_a_member_that_is_not_a_primitive(data, member):
    assert is_exact_type_match(data, member) is False
