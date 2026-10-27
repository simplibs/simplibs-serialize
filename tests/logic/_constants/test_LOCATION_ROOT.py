from simplibs.serialize.logic._constants import LOCATION_ROOT


def test_value():
    """The JSONPath symbol for the whole document."""
    assert LOCATION_ROOT == "$"
