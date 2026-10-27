from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import AlreadyExistsError

from simplibs.serialize import SerializationError
from simplibs.serialize.actions import DumpJsonFile, LoadJsonFile


@dataclass
class Point:
    x: int
    y: int


class Unknown:
    """Nothing knows this class."""


def _text(path: Path) -> str:
    """The exact text of the file, as it is on the disk."""
    return path.read_bytes().decode("utf-8")


def test_dump_json_file_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the DumpJsonFile action."""
    target = tmp_path / "out.json"
    assert_action(
        subtests,
        DumpJsonFile(path=target, indent=None),
        valid_values=[Point(1, 2), [1, 2]],
        expected_outputs=[target.resolve(), target.resolve()],
        invalid_values=[Unknown()],
        expected_exception_type=SerializationError,
        expected_input_type=Any,
        expected_output_type=Path,
        action_class=DumpJsonFile,
        invalid_init_params=[
            ((), {"path": target, "indent": []}),
            ((), {"path": target, "overwrite": "yes"}),
            ((), {"path": 5}),
        ],
        verbose=False,
    )


def test_dump_json_file_requires_a_path() -> None:
    with pytest.raises(TypeError):
        DumpJsonFile()


def test_dump_json_file_writes_the_object_that_flows_in(tmp_path) -> None:
    target = tmp_path / "point.json"

    result = DumpJsonFile(path=target)(Point(1, 2))

    assert _text(target) == '{\n  "x": 1,\n  "y": 2\n}\n'
    assert result.read_bytes() == target.read_bytes()


def test_dump_json_file_creates_the_folder(tmp_path) -> None:
    target = tmp_path / "a" / "b" / "point.json"

    DumpJsonFile(path=target, indent=None)(Point(1, 2))

    assert _text(target) == '{"x": 1, "y": 2}\n'


def test_dump_json_file_options_reach_the_function(tmp_path) -> None:
    target = tmp_path / "data.json"

    DumpJsonFile(path=target, indent=None, sort_keys=True, trailing_newline=False)({"b": 1, "a": 2})

    assert _text(target) == '{"a": 2, "b": 1}'


def test_dump_json_file_overwrite_off_refuses_a_second_write_and_keeps_the_first(tmp_path) -> None:
    action = DumpJsonFile(path=tmp_path / "data.json", indent=None, overwrite=False)
    action([1])

    with pytest.raises(AlreadyExistsError):
        action([2])

    assert _text(tmp_path / "data.json") == "[1]\n"


def test_dump_json_file_with_an_unsupported_object_writes_nothing(tmp_path) -> None:
    target = tmp_path / "new_folder" / "data.json"

    with pytest.raises(SerializationError):
        DumpJsonFile(path=target)(Unknown())

    assert not target.parent.exists()


def test_the_same_action_writes_whatever_flows_in(tmp_path) -> None:
    action = DumpJsonFile(path=tmp_path / "data.json", indent=None)

    action([1])
    action([2])

    assert _text(tmp_path / "data.json") == "[2]\n"


def test_dump_json_file_then_load_json_file_gives_the_object_back(tmp_path) -> None:
    pipeline = DumpJsonFile(path=tmp_path / "point.json") >> LoadJsonFile(annotation=Point)

    assert pipeline(Point(1, 2)) == Point(1, 2)
