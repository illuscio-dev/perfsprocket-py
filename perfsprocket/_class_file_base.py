import os
import shutil
from pathlib import Path
from typing import Generator, Union, Optional, cast, Tuple, TypeVar, Any

from perfsprocket import FileABC, NameABC
from perfsprocket._helpers_private import _init_path


SelfType = TypeVar("SelfType", bound="FileBase")


class FileBase(FileABC):
    def __init__(self, path: Union[str, Path], *args: Any):
        raise NotImplementedError

    def __iter__(self) -> Generator[Path, None, None]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __repr__(self) -> str:
        """<{Class Name}: '/{parent path}/{file name}'>"""
        return f"<{type(self).__name__}: '{self.path.parent / str(self.name)}'>"

    @property
    def path(self) -> Path:
        raise NotImplementedError

    @property
    def name(self) -> NameABC:
        raise NotImplementedError

    def init_new(self: SelfType, path_new: Path) -> SelfType:
        """initialize new object at end of copy or move."""
        raise NotImplementedError

    def move_iter(self: SelfType, dst_folder: Union[str, Path]) -> "BaseIterType":
        """
        Iterates through self, moving files to root level of dst_folder
        """
        dst_folder = _init_path(dst_folder)
        first: Optional[Path] = None

        for path in self:
            dst = dst_folder / path.name
            path.rename(dst)

            if first is None:
                first = dst

            yield dst

        first = cast(Path, first)
        yield self.init_new(first)

    def move(self: SelfType, dst_folder: Union[str, Path]) -> SelfType:
        """
        Executes :func:`FileBase.move_iter` and yield final item.
        """
        for item in self.move_iter(dst_folder):
            pass

        item = cast(SelfType, item)
        return item

    def copy_iter(self: SelfType, dst_folder: Union[str, Path]) -> "BaseIterType":
        """
        Iterates through self, copying files to root level of dst_folder
        """
        dst_folder = _init_path(dst_folder)
        first: Optional[Path] = None

        for path in self:
            dst = dst_folder / path.name
            shutil.copy(str(path), str(dst))

            if first is None:
                first = dst

            yield dst

        first = cast(Path, first)
        yield self.init_new(first)

    def copy(self: SelfType, dst_folder: Union[str, Path]) -> "SelfType":
        """
        Executes :func:`FileBase.copy_iter` and yields final item.
        """
        for item in self.copy_iter(dst_folder):
            pass

        item = cast(SelfType, item)
        return item

    def rename_iter(
        self: SelfType, name: Union[str, NameABC]
    ) -> Generator[Union[Tuple[Path, Path], SelfType], None, None]:
        raise NotImplementedError

    def rename(self: SelfType, name: Union[str, NameABC]) -> SelfType:
        """
        Executes :func:`FileBase.rename_iter` and yields final item.
        """
        for item in self.rename_iter(name):
            pass

        item = cast(SelfType, item)
        return item

    def delete_iter(self) -> Generator[Path, None, None]:
        """Iterates through self, deleting each path."""
        for path in self:
            os.remove(str(path))
            yield path

    def delete(self) -> None:
        """Executes :func:`delete_iter`."""
        for _ in self.delete_iter():
            pass

    def chmod_iter(self, mode: int) -> Generator[Path, None, None]:
        """Iterates through self, changing permissions on each path to ``mode``."""
        for path in self:
            path.chmod(mode)
            yield path

    def chmod(self, mode: int) -> None:
        """Executes :func:`FileBase.chmod_iter`."""
        for _ in self.chmod_iter(mode):
            pass


BaseIterType = Generator[Union[Path, SelfType], None, None]
