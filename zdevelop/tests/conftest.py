import pytest
import os
from pathlib import Path, PosixPath, WindowsPath
from typing import Tuple

from perfsprocket import File, FileSequence


@pytest.fixture
def single_file_for_operation(tmp_path) -> Tuple[File, Path]:
    """returns test file and destination directory"""
    src = Path(tmp_path) / "src" / "file.txt"
    dst = Path(tmp_path) / "dst"

    src.parent.mkdir(parents=True)
    dst.mkdir(parents=True)

    with src.open("w") as f:
        pass

    return File(src), dst


@pytest.fixture
def seq_path() -> Path:
    path = Path("/Volumes/disk/folder/file.100.txt")
    return path


@pytest.fixture
def seq_theory(seq_path) -> FileSequence:
    return FileSequence(seq_path, start=100, end=200)


@pytest.fixture
def file_seq_for_operation(tmp_path) -> Tuple[FileSequence, Path]:
    """returns test file sequence and destination directory"""

    src_folder = tmp_path / "src"
    dst_folder = Path(tmp_path) / "dst"

    src_folder.mkdir(parents=True)
    dst_folder.mkdir(parents=True)

    for i in range(100, 201):
        src_file = Path(tmp_path) / "src" / f"file.{i}.txt"
        with src_file.open("w") as f:
            f.write(str(i))

    init_path = Path(tmp_path) / "src" / "file.###.txt"
    return FileSequence(init_path, 100, 200), dst_folder


@pytest.fixture
def concrete_path():
    return PosixPath if os.name != "nt" else WindowsPath
