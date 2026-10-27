from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ConversionError, NotFoundError, ValidationError
from simplibs.path import PathLike

from simplibs.serialize import DeserializationError
from simplibs.serialize.actions import DumpJsonFile, LoadJsonFile


@dataclass
class Point:
    x: int
    y: int


def _write(path: Path, content: str | bytes) -> Path:
    """Put the exact bytes into a file."""
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    return path


def test_load_json_file_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the LoadJsonFile action."""
    good = _write(tmp_path / "good.json", '{"x": 1, "y": 2}')
    broken = _write(tmp_path / "broken.json", '{"x": 1,}')
    wrong_shape = _write(tmp_path / "wrong.json", '{"x": "a", "y": 2}')
    assert_action(
        subtests,
        LoadJsonFile(annotation=Point),
        valid_values=[good, str(good)],
        expected_outputs=[Point(1, 2), Point(1, 2)],
        invalid_values=[5, tmp_path / "missing.json", broken, wrong_shape],
        expected_exception_type=[ValidationError, NotFoundError, ConversionError, DeserializationError],
        expected_input_type=PathLike,
        expected_output_type=Any,
        action_class=LoadJsonFile,
        invalid_init_params=[
            ((), {"annotation": Point, "strict": "yes"}),
            ((), {"annotation": Point, "encoding": 5}),
        ],
        verbose=False,
    )


def test_load_json_file_requires_an_annotation() -> None:
    with pytest.raises(TypeError):
        LoadJsonFile()


def test_load_json_file_is_strict_by_default(tmp_path) -> None:
    path = _write(tmp_path / "point.json", '{"x": 1, "y": 2, "z": 3}')

    with pytest.raises(DeserializationError) as caught:
        LoadJsonFile(annotation=Point)(path)

    assert caught.value.error_name == "DESERIALIZE_UNKNOWN_FIELD"


def test_load_json_file_not_strict_ignores_unknown_keys(tmp_path) -> None:
    path = _write(tmp_path / "point.json", '{"x": 1, "y": 2, "z": 3}')

    assert LoadJsonFile(annotation=Point, strict=False)(path) == Point(1, 2)


def test_load_json_file_wrong_shape_has_the_location(tmp_path) -> None:
    path = _write(tmp_path / "point.json", '{"x": "a", "y": 2}')

    with pytest.raises(DeserializationError) as caught:
        LoadJsonFile(annotation=Point)(path)

    assert caught.value.label == "$.x"


def test_load_json_file_builds_the_configured_annotation(tmp_path) -> None:
    path = _write(tmp_path / "numbers.json", "[1, 2]")

    assert LoadJsonFile(annotation=list[int])(path) == [1, 2]


def test_load_json_file_reads_a_file_with_a_byte_order_mark_by_default(tmp_path) -> None:
    path = _write(tmp_path / "point.json", b'\xef\xbb\xbf{"x": 1, "y": 2}')

    assert LoadJsonFile(annotation=Point)(path) == Point(1, 2)


def test_the_same_action_loads_many_files(tmp_path) -> None:
    action = LoadJsonFile(annotation=Point)
    first = _write(tmp_path / "a.json", '{"x": 1, "y": 2}')
    second = _write(tmp_path / "b.json", '{"x": 3, "y": 4}')

    assert [action(first), action(second)] == [Point(1, 2), Point(3, 4)]


def test_dump_json_file_then_load_json_file_gives_the_object_back(tmp_path) -> None:
    pipeline = DumpJsonFile(path=tmp_path / "list.json") >> LoadJsonFile(annotation=list[Point])

    assert pipeline([Point(1, 2), Point(3, 4)]) == [Point(1, 2), Point(3, 4)]
