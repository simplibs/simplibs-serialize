import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import SerializationError
from simplibs.serialize.logic.serializer._validations import raise_unsupported_type_error


class _Point:
    """A value nobody knows how to convert."""


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_VALUES = [
    pytest.param(_Point(), "_Point", id="custom_class"),
    pytest.param(object(), "object", id="plain_object"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("obj, type_name", _VALUES)
def test_raise_unsupported_type_error_contract(subtests, obj, type_name, location, label) -> None:
    """Verify raise_unsupported_type_error produces a well-formed SerializationError card."""

    def raising_wrapper(target_location):
        raise_unsupported_type_error(target_location, obj)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=SerializationError,
        error_name="SERIALIZE_UNSUPPORTED_TYPE",
        label=label,
        value=obj,
        problem=f"No serializer is known for type '{type_name}'.",
        expected=(
            "A primitive, a list / tuple / set / mapping, a dataclass instance, "
            "a NamedTuple, an enum member, or a type that is built in or "
            "registered with register_type()."
        ),
        how_to_fix=(
            f"Register a handler: register_type({type_name}, to_func=...).",
            "Or pass `default=` to serialize() to deal with such objects in one place.",
            "Or convert the value yourself before serializing it.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
