from simplibs.serialize.logic._constants import FIELD_METADATA_KEY


def test_value():
    """The key is part of the format of hand-written field metadata, so it must not drift."""
    assert FIELD_METADATA_KEY == "simplibs.serialize"


def test_is_namespaced():
    """A dotted name keeps the key from colliding with the metadata of other tools."""
    assert "." in FIELD_METADATA_KEY
