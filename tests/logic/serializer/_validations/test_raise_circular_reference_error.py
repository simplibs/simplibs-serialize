import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_circular_reference_error


class _Node:
    """An object that can hold a reference to itself."""


def _list_with_itself() -> list:
    """A list that contains itself."""
    data: list = []
    data.append(data)
    return data


def _node_with_itself() -> _Node:
    """An object whose attribute leads back to itself."""
    node = _Node()
    node.parent = node
    return node


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_OBJECTS = [
    pytest.param(_list_with_itself(), "list", id="list"),
    pytest.param(_node_with_itself(), "_Node", id="object"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("obj, type_name", _OBJECTS)
def test_raise_circular_reference_error_contract(subtests, obj, type_name, location, label) -> None:
    """Verify raise_circular_reference_error produces a well-formed SerializationError card."""

    def raising_wrapper(target_location):
        raise_circular_reference_error(target_location, obj)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=SerializationError,
        error_name="SERIALIZE_CIRCULAR_REFERENCE",
        label=label,
        value=obj,
        problem=(
            f"This '{type_name}' contains itself, "
            "directly or through a handler, so it has no end."
        ),
        expected="Data without cycles — a tree, not a loop.",
        how_to_fix=(
            "Remove the reference that leads back (a parent link, for example).",
            "Exclude that field with serialized_field(exclude=True).",
            "Or let a handler write the object as an identifier instead of its content.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
