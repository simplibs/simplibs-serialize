import typing
from typing import Any, Final, NotRequired, Required

import pytest

from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._builders import build_qualified_value, build_value
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


_QUALIFIERS = [
    pytest.param(Final, id="Final"),
    pytest.param(Required, id="Required"),
    pytest.param(NotRequired, id="NotRequired"),
    pytest.param(
        getattr(typing, "ReadOnly", None),
        id="ReadOnly",
        marks=pytest.mark.skipif(not hasattr(typing, "ReadOnly"), reason="`ReadOnly` exists from Python 3.13"),
    ),
]


@pytest.mark.parametrize("qualifier", _QUALIFIERS)
def test_the_data_is_built_as_what_the_qualifier_wraps(qualifier):
    context, calls = _fake_context()

    build_qualified_value([1], qualifier[list[int]], ("items", 2), context)

    assert calls == [([1], list[int], ("items", 2))]


@pytest.mark.parametrize("qualifier", _QUALIFIERS)
def test_a_value_that_fits_the_wrapped_annotation_is_built(qualifier):
    assert build_qualified_value([1, 2], qualifier[list[int]], (), _real_context()) == [1, 2]


@pytest.mark.parametrize("qualifier", _QUALIFIERS)
def test_a_value_that_does_not_fit_is_the_card_of_the_wrapped_annotation(qualifier):
    with pytest.raises(DeserializationError) as caught:
        build_qualified_value([1, "x"], qualifier[list[int]], ("items",), _real_context())

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.items[1]"


def test_a_bare_qualifier_names_no_type_so_anything_goes():
    context, calls = _fake_context()

    build_qualified_value("anything", Final, (), context)

    assert calls == [("anything", Any, ())]
