from pathlib import Path, PurePath
from typing import Union


def _init_path(path: Union[str, PurePath]) -> Path:
    """Takes in path arg, if string, casts to Path"""
    if not isinstance(path, Path):
        path = Path(path)

    path = path.expanduser()
    return path


def _init_pure_path(path: Union[str, PurePath]) -> PurePath:
    """
    Takes in path arg, if string, casts to PurePath. Path objects are passed through,
    not cast back to PurePath.
    """
    if not isinstance(path, PurePath):
        path = PurePath(path)
    return path
