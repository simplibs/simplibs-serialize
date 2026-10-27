import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from simplibs.exception import AlreadyExistsError

from simplibs.serialize import SerializationError, dump_json_file


@dataclass
class Point:
    x: int
    y: int


class Unknown:
    """Nothing knows this class."""


def _text(path: Path) -> str:
    """The exact text of the file, as it is on the disk."""
    return path.read_bytes().decode("utf-8")


def test_a_dataclass_is_written_indented_with_a_trailing_newline(tmp_path):
    target = tmp_path / "point.json"

    dump_json_file(target, Point(1, 2))

    assert _text(target) == '{\n  "x": 1,\n  "y": 2\n}\n'


def test_the_return_value_is_the_path_of_the_written_file(tmp_path):
    target = tmp_path / "point.json"

    result = dump_json_file(target, Point(1, 2))

    assert isinstance(result, Path)
    assert result.name == "point.json"
    assert result.read_bytes() == target.read_bytes()


def test_a_path_given_as_text_is_accepted(tmp_path):
    result = dump_json_file(str(tmp_path / "point.json"), Point(1, 2))

    assert result.exists()


def test_the_folder_is_created_when_it_is_missing(tmp_path):
    target = tmp_path / "a" / "b" / "point.json"

    dump_json_file(target, Point(1, 2))

    assert json.loads(_text(target)) == {"x": 1, "y": 2}


def test_a_custom_type_is_written_through_default(tmp_path):
    target = tmp_path / "data.json"

    dump_json_file(target, {"a": Unknown()}, indent=None, default=lambda obj: "unknown")

    assert _text(target) == '{"a": "unknown"}\n'


def test_sort_keys_and_compact_output(tmp_path):
    target = tmp_path / "data.json"

    dump_json_file(target, {"b": 1, "a": 2}, indent=None, sort_keys=True)

    assert _text(target) == '{"a": 2, "b": 1}\n'


def test_the_trailing_newline_can_be_left_out(tmp_path):
    target = tmp_path / "data.json"

    dump_json_file(target, [1], indent=None, trailing_newline=False)

    assert _text(target) == "[1]"


def test_non_ascii_text_is_written_as_it_is_by_default(tmp_path):
    target = tmp_path / "data.json"

    dump_json_file(target, "č", indent=None)

    assert _text(target) == '"č"\n'


def test_an_existing_file_is_replaced_by_default(tmp_path):
    target = tmp_path / "data.json"
    target.write_text("old", encoding="utf-8")

    dump_json_file(target, [1], indent=None)

    assert _text(target) == "[1]\n"


def test_an_existing_file_is_an_error_when_overwrite_is_off_and_stays_as_it_was(tmp_path):
    target = tmp_path / "data.json"
    target.write_text("old", encoding="utf-8")

    with pytest.raises(AlreadyExistsError):
        dump_json_file(target, [1], overwrite=False)

    assert _text(target) == "old"


def test_a_value_that_cannot_be_written_fails_before_the_disk_is_touched(tmp_path):
    target = tmp_path / "data.json"
    target.write_text("old", encoding="utf-8")

    with pytest.raises(SerializationError) as caught:
        dump_json_file(target, {"items": [Unknown()]})

    assert caught.value.error_name == "SERIALIZE_UNSUPPORTED_TYPE"
    assert caught.value.label == "$.items[0]"
    assert _text(target) == "old"


def test_a_value_that_cannot_be_written_creates_no_file_and_no_folder(tmp_path):
    target = tmp_path / "new_folder" / "data.json"

    with pytest.raises(SerializationError):
        dump_json_file(target, Unknown())

    assert not target.parent.exists()


def test_nan_is_an_error_unless_it_is_allowed(tmp_path):
    target = tmp_path / "data.json"

    with pytest.raises(SerializationError) as caught:
        dump_json_file(target, [float("nan")])
    assert caught.value.error_name == "SERIALIZE_NON_FINITE_NUMBER"
    assert not target.exists()

    dump_json_file(target, [float("nan")], indent=None, allow_nan=True)
    assert _text(target) == "[NaN]\n"
