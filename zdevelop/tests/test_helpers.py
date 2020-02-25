import pytest
import os
from pathlib import (
    Path,
    PurePath,
    PosixPath,
    WindowsPath,
    PurePosixPath,
    PureWindowsPath,
)

from perfsprocket._helpers_private import _init_path, _init_pure_path


ConcretePath = PosixPath if os.name != "nt" else WindowsPath


@pytest.mark.parametrize(
    "path,path_type,answer,pass_not_implemented",
    [
        ("/dir/file.mov", str, Path() / "/" / "dir" / "file.mov", False),
        ("/Volumes/media/folder/file.mov", ConcretePath, None, True),
    ],
)
def test_init_path(path, path_type, answer, pass_not_implemented):
    path = path_type(path)

    result = _init_path(path)

    assert isinstance(result, Path)
    if isinstance(path, Path):
        assert isinstance(result, type(path))
        assert result is path
    else:
        assert result == answer
        assert isinstance(result, type(answer))


@pytest.mark.parametrize(
    "path,answer",
    [
        ("/dir/file.mov", PurePath() / "/" / "dir" / "file.mov"),
        (PurePath("/Volumes/media/folder/file.mov"), None),
        (PurePosixPath("/Volumes/media/folder/file.mov"), None),
        (PureWindowsPath(r"C:\media\folder\file.mov"), None),
        (Path("/Volumes/media/folder/file.mov"), None),
        (ConcretePath("/Volumes/media/folder/file.mov"), None),
    ],
)
def test_init_path_pure(path, answer):
    result = _init_pure_path(path)

    assert isinstance(result, PurePath)

    if isinstance(path, PurePath):
        assert isinstance(result, type(path))
        assert result is path
    else:
        assert result == answer
        assert isinstance(result, type(answer))
