from pathlib import Path, PurePath
from typing import Union, Generator, Tuple, TypeVar

from ._class_file_base import FileBase
from ._helpers_private import _init_path
from ._file_name import FileName, NameABC


SelfType = TypeVar("SelfType", bound="File")


class File(FileBase):
    def __init__(self, path: Union[str, PurePath]):
        """
        :param path: to file
        """
        path = _init_path(path)
        self._path: Path = path
        self._name: FileName = FileName.from_path(path)

    def __iter__(self) -> Generator[Path, None, None]:
        """Yields 1 path"""
        yield self.path

    def __len__(self) -> int:
        """
        Always ``1``
        """
        return 1

    @property
    def name(self) -> FileName:
        """{name}{ext}"""
        return self._name

    @property
    def path(self) -> Path:
        """path to file"""
        return self._path

    def init_new(self: SelfType, path_new: Path) -> SelfType:
        return type(self)(path_new)

    def rename_iter(
        self: SelfType, name: Union[str, NameABC]
    ) -> Generator[Union[Tuple[Path, Path], SelfType], None, None]:
        """Renames file. Yields new `File` as last object"""
        new_path = self.path.with_name(str(name))
        self.path.rename(new_path)
        yield self.path, new_path
        yield type(self)(new_path)
