import pytest

from simplibs.serialize.logic.serializer._helpers import to_primitive


class Name(str):
    """A str subclass that has its own idea of its text."""

    def __str__(self) -> str:
        return "Name(abc)"


class Port(int):
    """An int subclass that has its own idea of its number."""

    def __int__(self) -> int:
        return 0


class Ratio(float):
    """A float subclass that has its own idea of its number."""

    def __float__(self) -> float:
        return 0.0


@pytest.mark.parametrize(
    "obj, expected, kind",
    [
        pytest.param(Name("abc"), "abc", str, id="str_subclass"),
        pytest.param(Port(8080), 8080, int, id="int_subclass"),
        pytest.param(Ratio(1.5), 1.5, float, id="float_subclass"),
    ],
)
def test_gives_the_stored_value_as_the_exact_built_in_type(obj, expected, kind):
    result = to_primitive(obj)

    assert result == expected
    assert type(result) is kind


def test_a_plain_subclass_gives_its_value():
    class Plain(str):
        pass

    result = to_primitive(Plain("x"))

    assert result == "x"
    assert type(result) is str
