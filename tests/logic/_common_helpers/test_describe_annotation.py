import importlib
from typing import Annotated, Literal

import pytest

from simplibs.serialize.logic._common_helpers import describe_annotation


class Point:
    """A plain class used as an annotation."""


class _BrokenEngine:
    """A rule engine that cannot describe anything."""

    def __init__(self, annotation):
        raise RuntimeError("cannot describe")


@pytest.fixture
def broken_engine(monkeypatch):
    """Make the rule engine fail, so that only the fallbacks of describe_annotation are left."""
    # The package exports the function under the same name as its module, so the module is looked up by path
    module = importlib.import_module("simplibs.serialize.logic._common_helpers.describe_annotation")
    monkeypatch.setattr(module, "IsTyping", _BrokenEngine)


@pytest.mark.parametrize(
    "annotation, words",
    [
        pytest.param(Point, ["Point"], id="class"),
        pytest.param(int, ["int"], id="builtin"),
        pytest.param(list[int], ["list", "int"], id="subscripted_list"),
        pytest.param(int | None, ["int", "None"], id="optional"),
        pytest.param(Literal["a"], ["a"], id="literal"),
        pytest.param(Annotated[int, "doc"], ["int"], id="annotated"),
    ],
)
def test_names_what_was_asked_for(annotation, words):
    described = describe_annotation(annotation)

    assert isinstance(described, str)
    assert all(word in described for word in words)


@pytest.mark.parametrize("annotation", [5, "text", object(), None], ids=["int", "text", "object", "none"])
def test_never_fails_on_something_that_is_no_annotation(annotation):
    described = describe_annotation(annotation)

    assert isinstance(described, str)
    assert described


def test_fallback_for_a_plain_class_is_its_name(broken_engine):
    assert describe_annotation(Point) == "Point"


@pytest.mark.parametrize(
    "annotation",
    [list[int], int | None, Literal["a"], 5, "text"],
    ids=["subscripted_list", "union", "literal", "int", "text"],
)
def test_fallback_for_anything_else_is_its_repr(broken_engine, annotation):
    assert describe_annotation(annotation) == repr(annotation)
