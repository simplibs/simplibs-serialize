from collections.abc import Callable

import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._validations import raise_unsupported_annotation_error


class _Unregistered:
    """A plain class nobody registered a handler for."""


_LOCATIONS = [
    pytest.param((), "$", id="root"),
    pytest.param(("items", 2, "name"), "$.items[2].name", id="nested"),
]

_ANNOTATIONS = [
    pytest.param(Callable[..., int], id="callable"),
    pytest.param(_Unregistered, id="plain_class"),
]


@pytest.mark.parametrize("location, label", _LOCATIONS)
@pytest.mark.parametrize("annotation", _ANNOTATIONS)
def test_raise_unsupported_annotation_error_contract(subtests, annotation, location, label) -> None:
    """Verify raise_unsupported_annotation_error produces a well-formed DeserializationError card."""

    def raising_wrapper(target_location):
        raise_unsupported_annotation_error(target_location, annotation)

    exc = assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(location,),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_UNSUPPORTED_ANNOTATION",
        label=label,
        value=annotation,
        problem=f"No deserializer is available for the annotation {annotation!r}.",
        expected=(
            "A primitive, a container, a union, Annotated, Literal, an enum, a dataclass, "
            "a NamedTuple, a TypedDict, a NewType, or a type that is built in or "
            "registered with register_type()."
        ),
        how_to_fix=(
            f"Register a handler: register_type({annotation!r}, from_func=...).",
            "Or use a supported annotation for this field.",
        ),
        exception=TypeError,
        verbose=False,
    )

    # The tool compares labels as a substring, so the root `$` needs an exact check
    assert exc.label == label

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, TypeError)
