from simplibs.exception import ConversionError
from simplibs.exception.testing import assert_exception_class
from simplibs.serialize.exceptions import SerializeError


def test_serialize_error_basic_contract(subtests):
    """Runs the universal validation suite including inheritance from ConversionError."""
    assert_exception_class(
        subtests,
        SerializeError,
        expected_parents=ConversionError,
    )
