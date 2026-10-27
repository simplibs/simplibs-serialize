import pytest

from simplibs.serialize.annotations import JsonValue


def test_is_written_as_text_because_it_refers_to_itself():
    assert isinstance(JsonValue, str)


@pytest.mark.parametrize(
    "member",
    ["None", "bool", "int", "float", "str", "list[JsonValue]", "dict[str, JsonValue]"],
)
def test_names_every_json_kind(member):
    assert member in JsonValue
