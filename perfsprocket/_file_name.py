import re
from dataclasses import dataclass
from typing import Optional, Union, Dict, Tuple, overload, Any, cast
from typing_extensions import Protocol
from pathlib import PurePath

from ._helpers_private import _init_pure_path


class Braces:
    def __init__(self, open_char: str, close_char: str):
        self._open: str = open_char
        self._close: str = close_char

    def __repr__(self) -> str:
        return f"{self.open}{self.close}"

    @property
    def open(self) -> str:
        """opening character passed to :func:`Braces.__init__`"""
        return self._open

    @property
    def close(self) -> str:
        """closing character passed to :func:`Braces.__init__`"""
        return self._close

    def enclose(self, text: str) -> str:
        """wrap text in open and close char"""
        return f"{self.open}{text}{self.close}"


ARROW = Braces("<", ">")
BRACKET = Braces("[", "]")
CURLY = Braces("{", "}")
PAREN = Braces("(", ")")


BRACES_KINDS = [ARROW, BRACKET, CURLY, PAREN]


class Flag:
    pass


KEEP = Flag()


PATTERN = re.compile(
    r"^"
    r"(?P<base>.+)"
    r"(?P<sep>[._])"
    r"(?P<open>[\[{<(])?"
    r"(?P<start>\d+|#+)"
    r"(-(?P<end>\d*|#*))?"
    r"(?P<close>[\]}>)])?"
    r"(?P<extension>\..+)?"
    r"$"
)


class NameABC(Protocol):
    base: str
    extension: Optional[str]

    def __str__(self) -> str:
        return self.formatted()

    @classmethod
    def from_path(cls, path: Union[str, PurePath]) -> "NameABC":
        """New :class:`NameABC` instance from ``pathlib.Path`` or ``str``"""
        raise NotImplementedError

    def alter(
        self,
        base: Union[str, Flag] = KEEP,
        extension: Optional[Union[str, Flag]] = KEEP,
        **kwargs: Union[Any, Flag],
    ) -> "NameABC":
        """
        Returns new `NameABC` with changes to fields. Each argument should accept the
        ``perfsprocket.KEEP`` flag as the default, which signals that a value should not
        change. ``None`` values should be signals to change a field to ``None``. Methods
        should also include **kwargs so other Name conventions arguments can be passed
        without effect.
        """
        raise NotImplementedError

    def formatted(self) -> str:
        """Returns name string."""
        raise NotImplementedError


@dataclass(frozen=True)
class FileName(NameABC):
    base: str
    extension: Optional[str]

    def __post_init__(self) -> None:
        if self.extension is not None and not self.extension.startswith("."):
            object.__setattr__(self, "extension", f".{self.extension}")

    @classmethod
    def from_path(cls, path: Union[str, PurePath]) -> "FileName":
        """New :class:`FileName` instance from ``pathlib.Path`` or ``str``"""
        path = _init_pure_path(path)
        return FileName(base=path.stem, extension=path.suffix)

    def alter(
        self,
        base: Union[str, Flag] = KEEP,
        extension: Optional[Union[str, Flag]] = KEEP,
        **kwargs: Union[Any, Flag],
    ) -> "FileName":
        """
        Make changes to name.
        ``KEEP``: keep current value
        ``None``: Change value to ``None``

        :return: new object
        """
        # We can cast this since KEEP is the only Flag type defined.
        base_arg = self.base if base is KEEP else base
        base_arg = cast(str, base_arg)

        extension_arg = self.extension if extension is KEEP else extension
        extension_arg = cast(Optional[str], extension_arg)

        return FileName(base=base_arg, extension=extension_arg)

    def formatted(self) -> str:
        """returns formatted string EX: `movie.mp4`"""
        extension = self.extension if self.extension else ""
        return f"{self.base}{extension}"


@dataclass(frozen=True)
class SeqName(FileName):
    delim: Optional[str] = "."
    start: Union[int, str] = "#"
    end: Optional[Union[int, str]] = None
    pad: int = 0
    brackets: Optional[Braces] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "start", _post_init_start_end(self.start))
        object.__setattr__(self, "end", _post_init_start_end(self.end))

    @classmethod
    def from_path(cls, path: Union[str, PurePath]) -> "SeqName":
        """Parse file sequence filename from path"""
        path = _init_pure_path(path)
        pieces = _extract_pieces_from_str(path)
        base, delim, start, num_end, pad, brackets, extension = pieces

        new = cls(
            base=base,
            extension=extension,
            delim=delim,
            start=start,
            end=num_end,
            pad=pad,
            brackets=brackets,
        )
        return new

    def alter(
        self,
        base: Union[str, Flag] = KEEP,
        extension: Optional[Union[str, Flag]] = KEEP,
        delim: Union[str, Flag] = KEEP,
        start: Union[int, str, Flag] = KEEP,
        end: Optional[Union[int, str, Flag]] = KEEP,
        pad: Union[int, Flag] = KEEP,
        brackets: Optional[Union[Braces, Flag]] = KEEP,
        **kwargs: Union[Any, Flag],
    ) -> "SeqName":
        """
        Make changes to name.
        ``KEEP``: keep current value
        ``None``: Change value to ``None``

        :return: new object
        """
        new = base, extension, delim, start, end, pad, brackets
        names = ["base", "extension", "delim", "start", "end", "pad", "brackets"]

        kwargs = dict()

        for new_value, base in zip(new, names):
            if new_value is KEEP:
                new_value = getattr(self, base)
            kwargs[base] = new_value  # type: ignore

        # As long as params are typed correctly, we don't need to worry about type
        #   checks here.
        return SeqName(**kwargs)  # type: ignore

    def formatted(self) -> str:
        """returns formatted string EX: `A001_C001.[0034241-0034256].exr`"""
        open_bracket, close_bracket, range_sep = _format_range_pieces(self)
        start_str, end_str = _format_file_nums(self)
        ext = self.extension if self.extension else ""

        formatted = (
            f"{self.base}{self.delim}{open_bracket}{start_str}{range_sep}{end_str}"
            f"{close_bracket}{ext}"
        )

        return formatted


def _num_end_from_match(groups: Dict[str, Optional[str]]) -> Optional[Union[int, str]]:
    """extract end frame from REGEX match."""
    num_end: Optional[str] = groups["end"]
    if num_end:
        if "#" in num_end:
            result: Optional[Union[int, str]] = "#"
        else:
            result = int(num_end)
    else:
        result = None
    return result


def _padding_from_match(groups: Dict[str, Optional[str]]) -> int:
    """deduces padding from REGEX match"""
    start = groups["start"]
    start = cast(str, start)

    padding = len(start)

    return padding


def _brackets_from_match(groups: Dict[str, Optional[str]]) -> Optional[Braces]:
    """converts regex match to Brackets object"""
    open_char = groups["open"]
    close_char = groups["close"]

    if open_char is None and close_char is None:
        return None

    for this_bracket in BRACES_KINDS:
        if open_char != this_bracket.open:
            continue
        elif close_char != this_bracket.close:
            continue
        return this_bracket

    raise ValueError(f"Bracket Type: {open_char}{close_char} Not Recognized")


def _format_range_pieces(seq_name: "SeqName") -> Tuple[str, str, str]:
    """
    Returns open_bracket, close_bracket, range_separator. Non-relevant pieces are
    returned as empty string so concatenation does not need to run checks.
    """
    open_bracket = ""
    close_bracket = ""
    range_sep = ""

    if seq_name.end is not None:
        range_sep = "-"

        if seq_name.brackets is not None:
            open_bracket = seq_name.brackets.open
            close_bracket = seq_name.brackets.close

    return open_bracket, close_bracket, range_sep


def _format_file_nums(seq_name: "SeqName") -> Tuple[str, str]:
    fill_start = "#" if seq_name.start == "#" else "0"
    fill_end = "#" if seq_name.end == "#" else "0"

    start_str = str(seq_name.start).rjust(seq_name.pad, fill_start)

    if seq_name.end is not None:
        end_str = str(seq_name.end).rjust(seq_name.pad, fill_end)
    else:
        end_str = ""

    return start_str, end_str


def _run_filename_regex(path: PurePath) -> Dict[str, Optional[str]]:
    """extracts sequence name parts from regex"""
    file_name = path.name

    result = re.match(PATTERN, file_name)
    if result is None:
        raise ValueError

    # Stub file for re is wrong here. None can be a value if group is optional.
    #   We need to ignore MyPy complaining that Optional[str] is incorrect
    groups: Dict[str, Optional[str]] = result.groupdict()  # type: ignore
    return groups


PiecesType = Tuple[
    str,
    str,
    Union[int, str],
    Optional[Union[int, str]],
    int,
    Optional[Braces],
    Optional[str],
]


def _extract_pieces_from_str(path: PurePath) -> PiecesType:
    """extracts filename pieces from regex"""
    groups = _run_filename_regex(path)

    num_end = _num_end_from_match(groups)
    padding = _padding_from_match(groups)
    brackets = _brackets_from_match(groups)

    # need to do some casting shenanigans since our regex guarantees some returns
    base = groups["base"]
    base = cast(str, base)

    extension = groups["extension"]
    sep = groups["sep"]

    start = groups["start"]
    start = cast(str, start)

    if "#" in start:
        start_arg: Union[int, str] = "#"
    else:
        start_arg = int(start)

    sep = cast(str, sep)

    return base, sep, start_arg, num_end, padding, brackets, extension


@overload
def _post_init_start_end(value: None) -> None:
    ...


@overload  # noqa: F811
def _post_init_start_end(value: Union[int, str]) -> Union[int, str]:
    ...


def _post_init_start_end(  # noqa: F811
    value: Optional[Union[int, str]]
) -> Optional[Union[int, str]]:
    """
    parses start and end values, returns int when castable, raises value error if
    not and string is not "#"
    """
    if value is None:
        return None
    if isinstance(value, str):
        if "#" in value:
            return "#"
        else:
            raise ValueError("start/end must be int or '#'")
    else:
        return value
