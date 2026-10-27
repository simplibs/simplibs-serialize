from simplibs.exception.testing import assert_exception_class
from simplibs.serialize.exceptions import DeserializationError, SerializationError, SerializeError


def test_serialization_error_basic_contract(subtests):
    """Runs the universal validation suite including inheritance from SerializeError."""
    assert_exception_class(
        subtests,
        SerializationError,
        expected_parents=SerializeError,
    )


def test_serialization_error_is_not_a_deserialization_error():
    """The two directions stay apart, so a caller can catch only one half of the library."""
    assert not issubclass(SerializationError, DeserializationError)
