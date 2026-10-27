from simplibs.exception.testing import assert_exception_function
from simplibs.serialize import DeserializationError
from simplibs.serialize.logic.deserializer._validations import raise_data_too_deep_error


def test_raise_data_too_deep_error_contract(subtests) -> None:
    """Verify raise_data_too_deep_error produces a well-formed DeserializationError card."""
    exc = assert_exception_function(
        subtests,
        raise_data_too_deep_error,
        invalid_params=(),
        exception_type=DeserializationError,
        error_name="DESERIALIZE_DATA_TOO_DEEP",
        label="data",
        problem="The data is nested too deep to build.",
        expected="Data of reasonable depth.",
        how_to_fix=(
            "Check where the data comes from — real data is rarely a thousand levels deep.",
            "Flatten extremely deep data before deserializing it.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # The card must be catchable as the stdlib type it wraps
    assert isinstance(exc, ValueError)
