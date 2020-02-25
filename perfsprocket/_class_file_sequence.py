from pathlib import Path
from typing import Union, List, overload, Generator, Tuple, Optional, TypeVar

from perfsprocket import FileBase
from ._file_name import SeqName, NameABC, BRACKET
from ._helpers_private import _init_path


def seq_get_index(seq: "FileSequence", item: int) -> Path:
    print(str(seq.name), seq.start, seq.end, item)
    if item < 0:
        num = seq._end + item + 1
    else:
        num = seq._start + item

    if num < seq._start or num > seq.end:
        raise IndexError

    name = str(seq._name.alter(start=num, end=None))
    return seq._parent / name


def seq_get_slice(seq: "FileSequence", bounds: slice) -> "FileSequence":
    num_list: List[int] = list(range(seq._start, seq._end + 1))[bounds]
    return FileSequence(seq.path, num_list[0], num_list[-1])


@overload
def filenum_index(index: None, seq: "FileSequence") -> None:
    pass


@overload  # noqa: F811
def filenum_index(index: int, seq: "FileSequence") -> int:
    pass


def filenum_index(  # noqa: F811
    index: Optional[int], seq: "FileSequence"
) -> Optional[int]:
    """Converts file number to conventional index"""
    if index is None:
        return None
    if index < 0:
        return index
    else:
        index -= seq.start
        # if the requested index was a positive number, and adjusting for the start
        #   number throws it into the negatives, then we know the request is out of
        #   range of the sequence, so we need to raise an error here to avoid returning
        #   a file from the end of the sequence because of the negative roll over.
        if index < 0:
            raise IndexError("Frame Out of range")
        else:
            return index


class _SeqNumSlicer:
    def __init__(self, seq: "FileSequence"):
        self._seq: "FileSequence" = seq

    @overload
    def __getitem__(self, item: int) -> Path:
        ...

    @overload
    def __getitem__(self, item: slice) -> "FileSequence":  # noqa: F811
        ...

    def __getitem__(  # noqa: F811
        self, item: Union[int, slice]
    ) -> Union[Path, "FileSequence"]:
        index: Union[int, slice]

        if isinstance(item, int):
            index = filenum_index(item, self._seq)
        else:
            start = filenum_index(item.start, self._seq)
            stop = filenum_index(item.stop, self._seq)
            index = slice(start, stop, item.step)

        return self._seq[index]


SelfType = TypeVar("SelfType", bound="FileSequence")


class FileSequence(FileBase):
    def __init__(self, path: Union[str, Path], start: int, end: int):
        """
        Interact with file sequences.

        :param path: path to one (or generic) file in sequence.
            Generic path like so: 'photo_###.jpeg'
        :param start: first file number of sequence.
        :param end: last file number of sequence.
        """
        path = _init_path(path)
        name = SeqName.from_path(path).alter(start="#", end=None)

        self._parent: Path = path.parent
        self._name: SeqName = name

        self._start: int = start
        self._end: int = end

        self._seq_num_slicer: Optional["_SeqNumSlicer"] = None

    def __repr__(self) -> str:
        name = self.name.alter(start=self.start, end=self.end, brackets=BRACKET)
        return f"<{type(self).__name__}: '{self.path.parent / str(name)}'>"

    def __len__(self) -> int:
        return self._end - self._start + 1

    @overload
    def __getitem__(self, item: int) -> Path:
        ...

    @overload
    def __getitem__(self, item: slice) -> "FileSequence":  # noqa: F811
        ...

    def __getitem__(  # noqa: F811
        self, item: Union[int, slice]
    ) -> Union[Path, "FileSequence"]:
        if isinstance(item, slice):
            return seq_get_slice(self, item)
        else:
            return seq_get_index(self, item)

    def __iter__(self) -> Generator[Path, None, None]:
        for i in range(len(self)):
            yield self[i]

    def __reversed__(self) -> Generator[Path, None, None]:
        for i in reversed(range(len(self))):
            yield self[i]

    @property
    def path(self) -> Path:
        """path to first file"""
        return self[0]

    @property
    def name(self) -> SeqName:
        """dataclass with file sequence name info. See :class:`SeqName` documentation"""
        return self._name

    @property
    def start(self) -> int:
        """Return ``start`` frame num passed to :func:`FileSequence.__init__`"""
        return self._start

    @property
    def end(self) -> int:
        """Return ``end`` frame num passed to :func:`FileSequence.__init__`"""
        return self._end

    @property
    def files(self) -> _SeqNumSlicer:
        """Returns object that can get file by frame number index."""
        if self._seq_num_slicer is None:
            self._seq_num_slicer = _SeqNumSlicer(self)
        return self._seq_num_slicer

    def init_new(self: SelfType, path_new: Path) -> SelfType:
        return type(self)(path_new, self._start, self._end)

    def rename_iter(
        self, name: Union[str, NameABC]
    ) -> Generator[Union[Tuple[Path, Path], "FileSequence"], None, None]:
        """
        Renames each file in file num order, yielding a OldPath, NewPath pair *after* it
        has been successfully moved. Yields new :class:`FileSequence` as last item.
        """
        if isinstance(name, str):
            name = SeqName.from_path(name)
        elif not isinstance(name, SeqName):
            name = SeqName(base=name.base, extension=name.extension)

        if isinstance(name.start, int):
            new_start = name.start
        else:
            new_start = self._start

        num: int
        path: Path

        first_path: Optional[Path] = None

        # this comparison is correct, since
        reverse_rename: bool = new_start < self._start

        # We need to rename form last to first if the start frame is higher. When a
        # sequence is being renamed to a higher start file, the rename will override
        # it's own files if done in order.

        new_end = new_start + len(self)
        num_range = range(new_start, new_end)
        if reverse_rename:
            path_iter = iter(self)
            num_iter = iter(num_range)
        else:
            path_iter = reversed(self)
            num_iter = reversed(num_range)

        for num, path in zip(num_iter, path_iter):
            this_name = name.alter(start=num, end=None)
            new_path = path.parent / str(this_name)
            path.rename(new_path)

            yield path, new_path

            if first_path is None:
                first_path = new_path

        if reverse_rename or first_path is None:
            first_path = new_path

        # type can be ignored here since we know all names generated with the above
        # will have an int fot this_name.start
        yield type(self)(first_path, new_start, new_end - 1)
