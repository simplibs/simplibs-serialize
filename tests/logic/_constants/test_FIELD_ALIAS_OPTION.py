from simplibs.serialize.logic._constants import FIELD_ALIAS_OPTION


def test_value():
    """The word is part of the format of hand-written field metadata, so it must not drift."""
    assert FIELD_ALIAS_OPTION == "alias"
