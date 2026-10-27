from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ValidationError
from simplibs.path import PathLike

from simplibs.serialize import SerializationError
from simplibs.serialize.actions import DumpJsonFileTo


@dataclass
class Settings:
    debug: bool = False
    level: int = 1


class Unknown:
    """Nothing knows this class."""


def _text(path: Path) -> str:
    """The exact text of the file, as it is on the disk."""
    return path.read_bytes().decode("utf-8")


def test_dump_json_file_to_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the DumpJsonFileTo action."""
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    assert_action(
        subtests,
        DumpJsonFileTo(obj=Settings(), indent=None),
        valid_values=[first, str(second)],
        expected_outputs=[first.resolve(), second.resolve()],
        invalid_values=[5],
        expected_exception_type=ValidationError,
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=DumpJsonFileTo,
        invalid_init_params=[
            ((), {"obj": 1, "indent": []}),
            ((), {"obj": 1, "overwrite": "yes"}),
        ],
        verbose=False,
    )


def test_dump_json_file_to_requires_an_object() -> None:
    with pytest.raises(TypeError):
        DumpJsonFileTo()


def test_dump_json_file_to_writes_the_configured_object_to_the_path_that_flows_in(tmp_path) -> None:
    target = tmp_path / "settings.json"

    result = DumpJsonFileTo(obj=Settings(debug=True))(target)

    assert _text(target) == '{\n  "debug": true,\n  "level": 1\n}\n'
    assert result.name == "settings.json"


def test_the_same_settings_are_written_to_every_path_of_a_list(tmp_path) -> None:
    action = DumpJsonFileTo(obj=Settings(), indent=None)
    targets = [tmp_path / "a.json", tmp_path / "sub" / "b.json"]

    results = [action(target) for target in targets]

    assert [_text(target) for target in targets] == ['{"debug": false, "level": 1}\n'] * 2
    assert [result.name for result in results] == ["a.json", "b.json"]


def test_dump_json_file_to_with_an_unsupported_object_writes_nothing(tmp_path) -> None:
    target = tmp_path / "new_folder" / "data.json"

    with pytest.raises(SerializationError):
        DumpJsonFileTo(obj=Unknown())(target)

    assert not target.parent.exists()
