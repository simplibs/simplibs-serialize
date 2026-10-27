from simplibs.serialize.logic._constants import FIELD_EXCLUDE_OPTION


def test_value():
    """The word is part of the format of hand-written field metadata, so it must not drift."""
    assert FIELD_EXCLUDE_OPTION == "exclude"
