from typing import Generator, Union, Tuple, Any, TypeVar
from typing_extensions import Protocol, runtime
from pathlib import Path

from ._file_name import NameABC


SelfType = TypeVar("SelfType", bound="FileABC")


@runtime
class FileABC(Protocol):
    def __init__(self, path: Union[str, Path], *args: Any):
        """First argument is always str or pathlib.Path object"""
        raise NotImplementedError

    def __iter__(self) -> Generator[Path, None, None]:
        """iterates through FileABC's paths, returning them"""
        raise NotImplementedError

    def __len__(self) -> int:
        """
        Number of paths contained in FileABC. Should match the number of objects yielded
        by :func:`FileABC.__iter___`
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    @property
    def path(self) -> Path:
        """
        Single path most representative of file.

        :return: pathlib path. See pathlib's documentation for available methods.
        """
        raise NotImplementedError

    @property
    def name(self) -> NameABC:
        """
        :class:`NameABC` breakdown of file name.
        """
        raise NotImplementedError

    def move_iter(self: SelfType, dst_folder: Union[str, Path]) -> "FileIterType":
        """
        Yield new paths created wile moving file to ``dst_folder``. Yield new
        :class:`FileABC` at end
        """
        raise NotImplementedError

    def move(self: SelfType, dst_folder: Union[str, Path]) -> SelfType:
        """
        Non-iter version of :func:`FileABC.move_iter`, returning only new
        :class:`FileABC`
        """
        raise NotImplementedError

    def copy_iter(self: SelfType, dst_folder: Union[str, Path]) -> "FileIterType":
        """
        Yield new paths created wile moving file to ``dst_folder``. Yield new
        :class:`FileABC` at end
        """
        raise NotImplementedError

    def copy(self: SelfType, dst_folder: Union[str, Path]) -> "SelfType":
        """
        Non-iter version of :func:`FileABC.copy_iter`, returning only new
        :class:`FileABC`
        """
        raise NotImplementedError

    def rename_iter(
        self: SelfType, name: Union[str, NameABC]
    ) -> Generator[Union[Tuple[Path, Path], SelfType], None, None]:
        """
        Yields tuple of old, new paths, then new :class:`FileABC`

        :param name: Either string or :class:`NameABC` with naming details.
        """
        raise NotImplementedError

    def rename(self: SelfType, name: Union[str, NameABC]) -> SelfType:
        """
        Non-iter version of :func:`FileABC.rename_iter`, returning only new
        :class:`FileABC`
        """
        raise NotImplementedError

    def delete_iter(self) -> Generator[Path, None, None]:
        """Yields paths being deleted as operation occurs"""
        raise NotImplementedError

    def delete(self) -> None:
        """Non-iter version of :func:`FileABC.rename_iter`, returns ``None``"""
        raise NotImplementedError

    def chmod_iter(self, mode: int) -> Generator[Path, None, None]:
        """Yields paths with altered permissions as operation occurs"""
        raise NotImplementedError

    def chmod(self, mode: int) -> None:
        """Non-iter version of :func:`FileABC.chmod_iter`, returns ``None``"""
        raise NotImplementedError


FileIterType = Generator[Union[Path, SelfType], None, None]
