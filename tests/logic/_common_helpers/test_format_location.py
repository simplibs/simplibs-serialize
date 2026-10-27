import pytest

from simplibs.serialize.logic._common_helpers import format_location


@pytest.mark.parametrize(
    "location, expected",
    [
        pytest.param((), "$", id="root_only"),
        pytest.param(("name",), "$.name", id="a_name"),
        pytest.param((0,), "$[0]", id="an_index"),
        pytest.param(("items", 2, "name"), "$.items[2].name", id="nested_mix"),
        pytest.param((1, 2), "$[1][2]", id="index_in_index"),
        pytest.param(("název",), "$.název", id="non_ascii_name"),
        pytest.param(("a.b",), "$['a.b']", id="key_with_dot"),
        pytest.param(("user name",), "$['user name']", id="key_with_space"),
        pytest.param(("user-name",), "$['user-name']", id="key_with_dash"),
        pytest.param(("",), "$['']", id="empty_key"),
        pytest.param(("1",), "$['1']", id="numeric_text_stays_a_name"),
        pytest.param(("it's",), "$[\"it's\"]", id="key_with_quote"),
        pytest.param(("a", "b-c", 0), "$.a['b-c'][0]", id="quoted_key_inside_a_path"),
    ],
)
def test_format_location(location, expected):
    assert format_location(location) == expected
