from simplibs.exception.testing import assert_exception_class
from simplibs.serialize.exceptions import DeserializationError, SerializationError, SerializeError


def test_deserialization_error_basic_contract(subtests):
    """Runs the universal validation suite including inheritance from SerializeError."""
    assert_exception_class(
        subtests,
        DeserializationError,
        expected_parents=SerializeError,
    )


def test_deserialization_error_is_not_a_serialization_error():
    """The two directions stay apart, so a caller can catch only one half of the library."""
    assert not issubclass(DeserializationError, SerializationError)
