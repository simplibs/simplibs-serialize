import pytest

from simplibs.serialize.logic._constants import JSON_PRIMITIVES


def test_value():
    assert JSON_PRIMITIVES == (str, int, float, bool)


@pytest.mark.parametrize("cls", [str, int, float, bool])
def test_contains_the_json_classes(cls):
    assert cls in JSON_PRIMITIVES


@pytest.mark.parametrize("cls", [type(None), bytes, list, dict, tuple, set], ids=lambda cls: cls.__name__)
def test_does_not_contain_anything_else(cls):
    assert cls not in JSON_PRIMITIVES


def test_a_subclass_is_not_a_primitive():
    """The exact type is compared, so a `str` subclass is not let through as plain text."""

    class Name(str):
        pass

    assert Name not in JSON_PRIMITIVES
