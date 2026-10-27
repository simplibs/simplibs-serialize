from simplibs.serialize.logic._common_helpers import Location


def test_is_a_tuple_of_names_and_indexes():
    assert Location == tuple[str | int, ...]
