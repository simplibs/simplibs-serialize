import pytest
from simplibs.rules import IsTyping, Rule

from simplibs.serialize.logic.deserializer._helpers import is_rule_like


def _is_positive(value):
    return value > 0


class _Callable:
    """An object that can be called."""

    def __call__(self, value):
        return True


class _Marker:
    """A class used as a marker in `Annotated`."""


def test_true_for_a_rule():
    assert is_rule_like(IsTyping(int)) is True


@pytest.mark.parametrize(
    "item",
    [lambda value: value > 0, _is_positive, _Callable()],
    ids=["lambda", "function", "object_with_call"],
)
def test_true_for_a_predicate(item):
    assert is_rule_like(item) is True


@pytest.mark.parametrize(
    "item",
    ["documentation", 5, None, ("a", "b"), {"a": 1}],
    ids=["text", "number", "none", "tuple", "dict"],
)
def test_false_for_plain_metadata(item):
    assert is_rule_like(item) is False


@pytest.mark.parametrize("item", [_Marker, Rule], ids=["marker_class", "rule_class"])
def test_false_for_a_class(item):
    """A class is callable, but it is not a predicate."""
    assert is_rule_like(item) is False
