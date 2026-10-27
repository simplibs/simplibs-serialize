from dataclasses import dataclass
from pathlib import Path

import pytest
from simplibs.exception import AccessError, ConversionError, NotFoundError, StateError

from simplibs.serialize import DeserializationError, dump_json_file, load_json_file


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Server:
    host: str
    port: int


@dataclass
class Config:
    servers: list[Server]


def _write(path: Path, content: str | bytes) -> Path:
    """Put the exact bytes into a file."""
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    return path


def test_a_valid_file_becomes_a_dataclass(tmp_path):
    path = _write(tmp_path / "point.json", '{"x": 1, "y": 2}')

    assert load_json_file(path, Point) == Point(1, 2)


def test_a_path_given_as_text_is_accepted(tmp_path):
    path = _write(tmp_path / "point.json", '{"x": 1, "y": 2}')

    assert load_json_file(str(path), Point) == Point(1, 2)


@pytest.mark.parametrize(
    "content, annotation, expected",
    [
        pytest.param("[1, 2]", list[int], [1, 2], id="list"),
        pytest.param('{"a": 1}', dict[str, int], {"a": 1}, id="dict"),
        pytest.param("5", int, 5, id="number"),
    ],
)
def test_a_file_becomes_what_the_annotation_asks_for(tmp_path, content, annotation, expected):
    assert load_json_file(_write(tmp_path / "data.json", content), annotation) == expected


def test_a_file_with_a_byte_order_mark_is_read_by_default(tmp_path):
    path = _write(tmp_path / "point.json", b'\xef\xbb\xbf{"x": 1, "y": 2}')

    assert load_json_file(path, Point) == Point(1, 2)


def test_non_ascii_text_survives(tmp_path):
    assert load_json_file(_write(tmp_path / "data.json", '"č"'), str) == "č"


# ---------- a file that is no JSON ----------

def test_a_file_with_invalid_json_is_a_conversion_error_from_the_file_library(tmp_path):
    path = _write(tmp_path / "broken.json", '{"x": 1,}')

    with pytest.raises(ConversionError) as caught:
        load_json_file(path, Point)

    assert not isinstance(caught.value, DeserializationError)


# ---------- valid JSON of the wrong shape ----------

def test_json_that_does_not_fit_the_type_is_a_card_with_the_location(tmp_path):
    path = _write(
        tmp_path / "config.json",
        '{"servers": [{"host": "a", "port": 1}, {"host": "b", "port": 2}, {"host": "c", "port": "x"}]}',
    )

    with pytest.raises(DeserializationError) as caught:
        load_json_file(path, Config)

    assert caught.value.error_name == "DESERIALIZE_WRONG_TYPE"
    assert caught.value.label == "$.servers[2].port"


def test_an_unknown_key_is_an_error_when_strict_and_ignored_when_not(tmp_path):
    path = _write(tmp_path / "point.json", '{"x": 1, "y": 2, "z": 3}')

    with pytest.raises(DeserializationError) as caught:
        load_json_file(path, Point)
    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"

    assert load_json_file(path, Point, strict=False) == Point(1, 2)


# ---------- a file that cannot be read ----------

def test_a_missing_file_is_a_not_found_error(tmp_path):
    with pytest.raises(NotFoundError):
        load_json_file(tmp_path / "missing.json", Point)


def test_a_folder_is_not_a_file_to_read(tmp_path):
    # Which of the file library's own errors a folder gives depends on the system
    with pytest.raises((StateError, AccessError, NotFoundError)):
        load_json_file(tmp_path, Point)


# ---------- with dump_json_file ----------

def test_what_dump_json_file_writes_load_json_file_reads_back(tmp_path):
    original = Config([Server("a", 1), Server("b", 2)])
    path = tmp_path / "config.json"

    dump_json_file(path, original)

    assert load_json_file(path, Config) == original
